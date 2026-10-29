#!/usr/bin/env bash
# 019-number-parsing — strip the decoration, then let awk read the number.
set -euo pipefail

src="${IN:?IN not set}/amounts.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F';' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function parse(raw,   s, neg) {
  ok = 1
  s = trim(raw); neg = 0
  if (s ~ /^\(.*\)$/) { neg = 1; s = substr(s, 2, length(s) - 2) }
  sub(/^[^0-9+.-]+/, "", s)
  gsub(/,/, "", s)
  sub(/%$/, "", s)
  s = trim(s)
  if (s !~ /^[+-]?(\.?[0-9]+(\.[0-9]*)?)([eE][+-]?[0-9]+)?$/) { ok = 0; return 0 }
  return (neg ? -1 : 1) * (s + 0)
}
NR == 1 { print "id,value"; next }
{
  if (trim($0) == "") next
  rows++
  v = parse($2)
  if (!ok) failed++
  else { parsed++; total += v }
  printf "%s,%s\n", trim($1), (ok ? sprintf("%.2f", v) : "")
}
END {
  summary = outdir "/summary.json"
  printf "{\"rows\":%d,\"parsed\":%d,\"failed\":%d,\"total\":%.2f}\n", rows, parsed, failed, total > summary
  close(summary)
}' "$src" > "$outdir/parsed.csv"
