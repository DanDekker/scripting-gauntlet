#!/usr/bin/env bash
# 030-pivot-melt — the header names the value columns; loop them per row.
set -euo pipefail

src="${IN:?IN not set}/wide.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 {
  cols = NF
  for (i = 2; i <= NF; i++) Q[i] = tolower(trim($i))
  next
}
{
  if (trim($0) == "") next
  reg = tolower(trim($1))
  if (!(reg in seen)) { seen[reg] = 1; regions++ }
  for (i = 2; i <= cols; i++) {
    v = trim($i)
    if (v == "") continue
    cells++
    total += v + 0
    printf "%s,%s,%.2f\n", reg, Q[i], v + 0
  }
}
END {
  summary = outdir "/summary.json"
  printf "{\"regions\":%d,\"cells\":%d,\"total\":%.2f}\n", regions, cells, total > summary
  close(summary)
}' "$src" | LC_ALL=C sort -t, -k1,1 -k2,2 > "$body"

{
  printf 'region,quarter,amount\n'
  cat "$body"
} > "$outdir/long.csv"
