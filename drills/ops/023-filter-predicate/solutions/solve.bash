#!/usr/bin/env bash
# 023-filter-predicate — trim, lowercase, one predicate, then sort.
set -euo pipefail

src="${IN:?IN not set}/orders.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v OFS=',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  oid  = trim($1)
  cust = trim($2)
  reg  = tolower(trim($3))
  st   = tolower(trim($4))
  amt  = trim($5)
  sub(/^\$/, "", amt)
  rows_in++
  if (st != "paid" || amt + 0 < 100) next
  if (reg != "west" && reg != "east" && reg != "north") next
  kept++
  total += amt + 0
  printf "%s,%s,%s,%s,%.2f\n", oid, cust, reg, st, amt + 0
}
END {
  summary = outdir "/summary.json"
  fmt = "{\"rows_in\":%d,\"kept\":%d,\"dropped\":%d,\"total\":%.2f}\n"
  printf fmt, rows_in, kept, rows_in - kept, total > summary
  close(summary)
}' "$src" | sort -t, -k5,5nr -k1,1 | {
  printf 'order_id,customer,region,status,amount\n'
  cat
} > "$outdir/kept.csv"
