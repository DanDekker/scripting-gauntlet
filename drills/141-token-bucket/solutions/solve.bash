#!/usr/bin/env bash
# Simulate the two buckets in awk: sort the valid requests first, then walk them.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

rpm_capacity=$(jq -r '.rpm_capacity' "$in_dir/config.json")
rpm_refill=$(jq -r '.rpm_refill_per_sec' "$in_dir/config.json")
tpm_capacity=$(jq -r '.tpm_capacity' "$in_dir/config.json")
tpm_refill=$(jq -r '.tpm_refill_per_sec' "$in_dir/config.json")

# Valid requests only, carrying their input line number for the tie-break.
valid=$(awk -F, '
  NR == 1 { next }
  {
    line = $0
    sub(/^[ \t\r]+/, "", line)
    sub(/[ \t\r]+$/, "", line)
    if (line == "") next
    if (split(line, f, ",") != 3) next
    for (i = 1; i <= 3; i++) { sub(/^[ \t]+/, "", f[i]); sub(/[ \t]+$/, "", f[i]) }
    if (f[1] == "" || f[2] !~ /^-?[0-9]+$/ || f[3] !~ /^-?[0-9]+$/) next
    if (f[3] + 0 < 0) next
    printf "%d\t%s\t%s\t%s\n", NR, f[1], f[2], f[3]
  }' "$in_dir/requests.csv" | LC_ALL=C sort -t $'\t' -k3,3n -k1,1n)

{
  printf 'id,timestamp,tokens,status,req_left,tok_left\n'
  printf '%s\n' "$valid" | awk -F'\t' \
    -v rcap="$rpm_capacity" -v rrps="$rpm_refill" \
    -v tcap="$tpm_capacity" -v trps="$tpm_refill" '
    BEGIN { req = rcap + 0; tok = tcap + 0; prev = "" }
    NF < 4 { next }
    {
      ts = $3 + 0
      need = $4 + 0
      dt = (prev == "" ? 0 : ts - prev)
      req += dt * rrps; if (req > rcap) req = rcap
      tok += dt * trps; if (tok > tcap) tok = tcap
      if (req >= 1.0 && tok >= need) {
        status = "accept"; req -= 1.0; tok -= need
      } else {
        status = "reject"
      }
      printf "%s\t%d\t%d\t%s\t%.2f\t%.2f\n", $2, ts, need, status, req, tok
      prev = ts
    }' | awk -F'\t' '{ printf "%s,%s,%s,%s,%s,%s\n", $1, $2, $3, $4, $5, $6 }'
} > "$out_dir/decisions.csv"

read -r total accepted rejected served refused < <(awk -F, 'NR > 1 {
  total++
  if ($4 == "accept") { accepted++; served += $3 } else { rejected++; refused += $3 }
} END { printf "%d %d %d %d %d\n", total, accepted, rejected, served, refused }' "$out_dir/decisions.csv")

jq -n \
  --argjson total_requests "$total" \
  --argjson accepted "$accepted" \
  --argjson rejected "$rejected" \
  --argjson tokens_served "$served" \
  --argjson tokens_rejected "$refused" \
  '{total_requests: $total_requests, accepted: $accepted, rejected: $rejected,
    tokens_served: $tokens_served, tokens_rejected: $tokens_rejected}' > "$out_dir/summary.json"
