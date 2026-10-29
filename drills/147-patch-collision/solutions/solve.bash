#!/usr/bin/env bash
# Lease collisions and a first-fit batch schedule. awk keeps the lease table in memory and
# does the O(n^2) checks; sort supplies every ordering the contract asks for.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# Every non-blank data row counts, valid or not.
total_leases=$(awk 'NR == 1 { next } /^[[:space:]]*$/ { next } { n++ } END { print n + 0 }' \
  "$in_dir/leases.csv")

awk -F, '
  function trim(s) { gsub(/^[ \t\r]+/, "", s); gsub(/[ \t\r]+$/, "", s); return s }
  NR == 1 { next }
  {
    if (trim($0) == "") next
    if (NF < 4) next
    agent = trim($1); file = trim($2); s = trim($3); e = trim($4)
    if (agent == "" || file == "") next
    if (s !~ /^[0-9]+$/ || e !~ /^[0-9]+$/) next
    s += 0; e += 0
    if (s < 1 || e < s) next
    print file "," agent "," s "," e
  }
' "$in_dir/leases.csv" \
  | LC_ALL=C sort -u \
  | LC_ALL=C sort -t, -k1,1 -k3,3n -k2,2 -k4,4n > "$scratch/leases.txt"

awk -F, '
  { n++; F[n] = $1; A[n] = $2; S[n] = $3 + 0; E[n] = $4 + 0 }
  END {
    for (i = 1; i <= n; i++)
      for (j = i + 1; j <= n; j++) {
        if (F[i] != F[j] || A[i] == A[j]) continue
        if (S[i] > E[j] || S[j] > E[i]) continue
        a = A[i]; b = A[j]; r1 = S[i] "-" E[i]; r2 = S[j] "-" E[j]
        if (a > b) { t = a; a = b; b = t; t = r1; r1 = r2; r2 = t }
        print F[i] "," a "," r1 "," b "," r2
      }
  }
' "$scratch/leases.txt" > "$scratch/collisions.txt"

{
  printf 'file,agent_1,range_1,agent_2,range_2\n'
  LC_ALL=C sort -t, -k1,1 -k2,2 -k4,4 "$scratch/collisions.txt"
} > "$out_dir/collisions.csv"

awk -F, -v batch_file="$scratch/batches" '
  { n++; F[n] = $1; A[n] = $2; S[n] = $3 + 0; E[n] = $4 + 0 }
  END {
    nb = 0
    for (i = 1; i <= n; i++) {
      placed = 0
      for (b = 1; b <= nb && !placed; b++) {
        ok = 1
        for (k = 1; k <= cnt[b]; k++) {
          x = mem[b, k]
          if (F[x] == F[i] && A[x] != A[i] && !(S[i] > E[x] || S[x] > E[i])) { ok = 0; break }
        }
        if (ok) { cnt[b]++; mem[b, cnt[b]] = i; placed = 1 }
      }
      if (!placed) { nb++; cnt[nb] = 1; mem[nb, 1] = i }
    }
    for (b = 1; b <= nb; b++)
      for (k = 1; k <= cnt[b]; k++) {
        x = mem[b, k]
        print b "," A[x] "," F[x] "," S[x] "-" E[x]
      }
    print nb > batch_file
  }
' "$scratch/leases.txt" > "$scratch/schedule.txt"

{
  printf 'batch,agent_id,file,range\n'
  LC_ALL=C sort -t, -k1,1n -k3,3 -k2,2 "$scratch/schedule.txt"
} > "$out_dir/schedule.csv"

valid_leases=$(wc -l < "$scratch/leases.txt" | tr -d ' ')
collision_pairs=$(wc -l < "$scratch/collisions.txt" | tr -d ' ')
total_batches=$(tr -d ' ' < "$scratch/batches")

jq -n \
  --argjson total_leases "$total_leases" \
  --argjson valid_leases "$valid_leases" \
  --argjson collision_pairs "$collision_pairs" \
  --argjson total_batches "$total_batches" \
  '{total_leases: $total_leases, valid_leases: $valid_leases,
    collision_pairs: $collision_pairs, total_batches: $total_batches}' \
  > "$out_dir/summary.json"
