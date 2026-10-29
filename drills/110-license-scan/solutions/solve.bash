#!/usr/bin/env bash
# Scan licences with awk: normalise, look the licence up in the policy, sort the rows.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

for f in deps.txt policy.csv; do
  [ -f "$in_dir/$f" ] || { printf 'missing %s/%s\n' "$in_dir" "$f" >&2; exit 1; }
 done

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk -F',' -v rows="$scratch/rows.csv" -v js="$scratch/summary.json" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
function norm(s,   t) { t = tolower(trim(s)); sub(/[ \t]*license$/, "", t); return trim(t) }
FILENAME == ARGV[1] {
  if (FNR == 1) next
  line = trim($0)
  if (line == "") next
  pol[norm($1)] = (tolower(trim($2)) == "yes") ? "yes" : "no"
  next
}
{
  line = trim($0)
  if (line == "") { skipped++; next }
  nf = split(line, f, /[ \t]+/)
  if (nf == 4 && tolower(f[4]) == "license") { f[3] = f[3] " " f[4]; nf = 3 }
  if (nf != 3) { skipped++; next }
  nv++
  nm[nv] = f[1]
  vr[nv] = f[2]
  lc[nv] = norm(f[3])
  if (!(lc[nv] in pol)) st[nv] = "unknown"
  else st[nv] = (pol[lc[nv]] == "yes") ? "allowed" : "denied"
}
END {
  for (i = 1; i <= nv; i++) pair[nm[i], vr[i]] = 1
  for (k in pair) { split(k, kp, SUBSEP); distinct[kp[1]]++ }
  conflicts = 0
  for (k in distinct) if (distinct[k] > 1) conflicts++

  for (i = 1; i <= nv; i++) {
    printf "%s,%s,%s,%s\n", nm[i], vr[i], lc[i], st[i] > rows
    if (st[i] == "allowed") allowed++
    else if (st[i] == "denied") denied++
    else unknown++
  }
  close(rows)

  printf "{\n" > js
  printf "  \"deps\": %d,\n", nv > js
  printf "  \"skipped\": %d,\n", skipped > js
  printf "  \"allowed\": %d,\n", allowed > js
  printf "  \"denied\": %d,\n", denied > js
  printf "  \"unknown\": %d,\n", unknown > js
  printf "  \"conflicts\": %d\n", conflicts > js
  printf "}\n" > js
  close(js)
}
' "$in_dir/policy.csv" "$in_dir/deps.txt"

{
  printf 'name,version,licence,status\n'
  LC_ALL=C sort -s -t, -k1,1 -k2,2 "$scratch/rows.csv"
} > "$out_dir/deps.csv"

cp "$scratch/summary.json" "$out_dir/summary.json"
