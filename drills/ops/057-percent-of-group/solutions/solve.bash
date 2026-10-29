#!/usr/bin/env bash
# 057-percent-of-group — totals first, one sort, then the ordered walk.
set -euo pipefail

src="${IN:?IN not set}/sales.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
totals=$(mktemp)
trap 'rm -f "$body" "$body.sorted" "$totals"' EXIT

awk -F',' -v outdir="$outdir" -v totals="$totals" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  reg = tolower(trim($1)); rep = trim($2); amt = trim($3) + 0
  rows++; grand += amt
  tot[reg] += amt
  printf "%s,%s,%.2f\n", reg, rep, amt
}
END {
  for (r in tot) print r "," tot[r] > totals
  summary = outdir "/summary.json"
  printf "{\"rows\":%d,\"groups\":%d,\"total\":%.2f}\n", rows, length(tot), grand > summary
  close(summary); close(totals)
}' "$src" > "$body"

LC_ALL=C sort -t, -k1,1 -k3,3nr -k2,2 "$body" > "$body.sorted"

{
  printf 'region,rep,amount,pct,cum_pct\n'
  awk -F',' -v totals="$totals" '
  NR == FNR { total[$1] = $2; next }
  {
    running[$1] += $3
    printf "%s,%s,%.2f,%.2f,%.2f\n", $1, $2, $3, 100 * $3 / total[$1], 100 * running[$1] / total[$1]
  }' "$totals" "$body.sorted"
} > "$outdir/shares.csv"
