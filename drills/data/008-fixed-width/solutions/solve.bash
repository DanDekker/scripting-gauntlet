#!/usr/bin/env bash
# 008-fixed-width — slice the record, do not split it.
set -euo pipefail

src="${IN:?IN not set}/inventory.dat"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
BEGIN { inv = outdir "/inventory.csv"; print "name,dept,qty,price,total" > inv }
{
  name  = trim(substr($0, 1, 8))
  dept  = trim(substr($0, 9, 6))
  qty   = trim(substr($0, 15, 4))
  price = trim(substr($0, 19, 9))

  if (name == "") blank++
  total = qty * price
  printf "%s,%s,%s,%.2f,%.2f\n", name, dept, qty, price, total > inv
  records++
}
END {
  close(inv)
  sum = outdir "/summary.json"
  printf "{\"records\":%d,\"blank_names\":%d}\n", records, blank > sum
  close(sum)
}' "$src"
