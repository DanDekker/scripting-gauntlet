#!/usr/bin/env bash
# 006-ragged-rows — pad short rows, drop surplus fields, count both.
set -euo pipefail

src="${IN:?IN not set}/orders.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v OFS=',' -v outdir="$outdir" '
NR == 1 { width = NF; print; next }
{
  if (NF < width) {
    for (i = NF + 1; i <= width; i++) $i = ""
    padded++
  } else if (NF > width) {
    NF = width
    truncated++
  }
  rows++
  print
}
END {
  summary = outdir "/summary.json"
  printf "{\"rows\":%d,\"padded\":%d,\"truncated\":%d}\n", rows, padded, truncated > summary
  close(summary)
}' "$src" > "$outdir/clean.csv"
