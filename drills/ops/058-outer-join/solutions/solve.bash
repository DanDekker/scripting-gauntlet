#!/usr/bin/env bash
# 058-outer-join — load the left side, stream the right, then sweep the leftovers.
set -euo pipefail

left="${IN:?IN not set}/left.csv"
right="${IN:?IN not set}/right.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == FNR {
  if (FNR == 1 || trim($0) == "") next
  k = tolower(trim($1))
  name[k] = trim($2); qty[k] = trim($3); inleft[k] = 1
  next
}
{
  if (FNR == 1 || trim($0) == "") next
  k = tolower(trim($1))
  price[k] = trim($2); inright[k] = 1
}
END {
  for (k in inleft) {
    if (k in inright) { both++; side = "both" }
    else { left_only++; side = "left" }
    q = qty[k] + 0
    if (k in inright) pr = sprintf("%.2f", price[k] + 0); else pr = ""
    printf "%s,%s,%d,%s,%s\n", k, name[k], q, pr, side
  }
  for (k in inright) {
    if (k in inleft) continue
    right_only++
    printf "%s,,,%.2f,right\n", k, price[k] + 0
  }
  summary = outdir "/summary.json"
  printf "{\"keys\":%d,\"both\":%d,\"left_only\":%d,\"right_only\":%d}\n", both + left_only + right_only, both, left_only, right_only > summary
  close(summary)
}' "$left" "$right" | LC_ALL=C sort -t, -k1,1 > "$body"

{
  printf 'sku,name,qty,price,side\n'
  cat "$body"
} > "$outdir/joined.csv"
