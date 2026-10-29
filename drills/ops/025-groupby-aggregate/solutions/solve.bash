#!/usr/bin/env bash
# 025-groupby-aggregate — composite key, one accumulator, sort at the end.
set -euo pipefail

src="${IN:?IN not set}/sales.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  rows_in++
  amt = trim($4)
  if (amt == "") { skipped++; next }
  reg = tolower(trim($2))
  mon = substr(trim($1), 1, 7)
  key = reg SUBSEP mon
  if (!(key in seen)) {
    seen[key] = 1
    n++
    R[n] = reg
    M[n] = mon
  }
  orders[key]++
  revenue[key] += amt + 0
}
END {
  total = 0
  for (i = 1; i <= n; i++) {
    key = R[i] SUBSEP M[i]
    total += revenue[key]
    printf "%s,%s,%d,%.2f,%.2f\n", R[i], M[i], orders[key], revenue[key], revenue[key] / orders[key]
  }
  summary = outdir "/summary.json"
  printf "{\"rows_in\":%d,\"skipped\":%d,\"groups\":%d,\"revenue\":%.2f}\n", rows_in, skipped, n, total > summary
  close(summary)
}' "$src" | sort -t, -k1,1 -k2,2 > "$outdir/body.csv"

{
  printf 'region,month,orders,revenue,avg_order\n'
  cat "$outdir/body.csv"
} > "$outdir/rollup.csv"
rm -f "$outdir/body.csv"
