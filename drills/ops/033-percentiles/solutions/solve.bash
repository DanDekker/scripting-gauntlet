#!/usr/bin/env bash
# 033-percentiles — sort by endpoint then duration, then index into each run.
set -euo pipefail

src="${IN:?IN not set}/latency.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F',' '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  printf "%s,%d\n", tolower(trim($1)), trim($2) + 0
}' "$src" | LC_ALL=C sort -t, -k1,1 -k2,2n | awk -F',' -v outdir="$outdir" '
function flush(   n, i50, i90) {
  if (ep == "") return
  n = cnt
  i50 = int((50 * n + 99) / 100)
  i90 = int((90 * n + 99) / 100)
  printf "%s,%d,%d,%d,%d\n", ep, n, V[i50], V[i90], V[n]
  if (V[n] > slowest) slowest = V[n]
  endpoints++
  requests += n
}
$1 != ep { flush(); ep = $1; cnt = 0 }
{ cnt++; V[cnt] = $2 }
END {
  flush()
  summary = outdir "/summary.json"
  printf "{\"endpoints\":%d,\"requests\":%d,\"slowest\":%d}\n", endpoints, requests, slowest > summary
  close(summary)
}' > "$body"

{
  printf 'endpoint,count,p50,p90,max\n'
  cat "$body"
} > "$outdir/latency.csv"
