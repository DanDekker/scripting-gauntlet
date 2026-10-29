#!/usr/bin/env bash
# 012-markdown-table — grep the pipe lines, drop the separator, trim the cells.
set -euo pipefail

src="${IN:?IN not set}/report.md"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -v outdir="$outdir" '
/^\|/ {
  if ($0 ~ /^\|[-: |]+\|$/) next          # separator row, not data
  n = split($0, cell, "|")
  for (i = 2; i <= n - 1; i++) {
    gsub(/^[ \t]+|[ \t]+$/, "", cell[i])
  }
  if (header == 0) { print "region,qty,revenue"; header = 1; next }
  printf "%s,%d,%.2f\n", cell[2], cell[3] + 0, cell[4] + 0
  rows++
  qty += cell[3]
  revenue += cell[4]
  next
}
END {
  summary = outdir "/summary.json"
  printf "{\"rows\":%d,\"total_qty\":%d,\"total_revenue\":%.2f}\n", rows, qty, revenue > summary
  close(summary)
}' "$src" > "$outdir/table.csv"
