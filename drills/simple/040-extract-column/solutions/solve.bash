#!/usr/bin/env bash
# 040-extract-column — read the header, keep the index, print that field.
set -euo pipefail

src="${IN:?IN not set}/servers.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
NR == 1 {
  for (i = 1; i <= NF; i++) if (trim($i) == "host") col = i
  if (!col) { print "servers.csv: no host column in header" > "/dev/stderr"; exit 1 }
  next
}
{
  line = trim($0)
  if (line == "" || line ~ /^#/) { skipped++; next }
  print trim($col)
  rows++
}
END {
  if (!col) exit 1
  f = outdir "/summary.json"
  printf "{\"rows\":%d,\"skipped\":%d}\n", rows, skipped > f
  close(f)
}' "$src" > "$outdir/hosts.txt"
