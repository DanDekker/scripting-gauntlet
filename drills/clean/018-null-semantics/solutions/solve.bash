#!/usr/bin/env bash
# 018-null-semantics — one token list, one case fold, one counter.
set -euo pipefail

src="${IN:?IN not set}/people.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v OFS=',' -v summary="$outdir/summary.json" '
function isnull(v,   t) {
  t = tolower(v)
  return (t == "" || t == "na" || t == "n/a" || t == "null" || t == "-")
}
NR == 1 { print; next }
{
  for (i = 1; i <= NF; i++) {
    if (isnull($i)) { $i = ""; nulls++ }
  }
  rows++
  print
}
END {
  printf "{\"rows\":%d,\"nulls\":%d}\n", rows, nulls > summary
  close(summary)
}' "$src" > "$outdir/clean.csv"
