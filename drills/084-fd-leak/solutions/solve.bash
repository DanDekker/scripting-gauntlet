#!/usr/bin/env bash
# 084-fd-leak - sort into series, then one pass per group.
set -euo pipefail
export LC_ALL=C

src="${IN:?IN not set}/fd-samples.csv"
outdir="${OUT:?OUT not set}"
[[ -r "$src" ]] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F, '
  NR == 1 || $1 == "sample" { next }
  NF != 3 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ || $3 !~ /^[0-9]+$/ { next }
  { printf "%d,%d,%d\n", $2, $1, $3 }
' "$src" | LC_ALL=C sort -t, -k1,1n -k2,2n | awk -F, -v body="$body" -v outdir="$outdir" '
function flush(   rate, mono) {
  if (pid == "") return
  if (n < 2) { skipped++; return }
  rate = (lastv - firstv) / (lasts - firsts)
  mono = (dips == 0) ? "true" : "false"
  printf "%d,%d,%d,%.1f,%s\n", pid, firstv, lastv, rate, mono > body
  measured++
  if (dips == 0 && rate >= 5.0) leaking++
}
$1 != pid { flush(); pid = $1; n = 0; dips = 0 }
{
  n++
  if (n == 1) { firstv = $3; firsts = $2 }
  else if ($3 < lastv) dips++
  lastv = $3; lasts = $2
}
END {
  flush()
  close(body)
  printf "{\"pids\":%d,\"leaking\":%d,\"skipped\":%d}\n", measured, leaking, skipped \
    > (outdir "/summary.json")
  close(outdir "/summary.json")
}' 2>/dev/null || true

{
  printf 'pid,first_fds,last_fds,fds_per_min,monotonic\n'
  LC_ALL=C sort -t, -k4,4nr -k1,1n "$body"
} > "$outdir/leaks.csv"
