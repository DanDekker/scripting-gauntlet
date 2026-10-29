#!/usr/bin/env bash
# 131-port-scan-triage - awk the baseline into TSV, awk the scan into rows keyed by
# port<TAB>proto, then let sort do the numeric-port ordering.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
for f in scan.txt baseline.csv; do
  [[ -r "$inp/$f" ]] || { echo "missing $inp/$f" >&2; exit 1; }
done
mkdir -p "$outdir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# --- baseline: port<TAB>service<TAB>expected, trimmed, header and blanks dropped ----
awk -F',' -v src="$inp/baseline.csv" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
{
  line = trim($0)
  if (line == "") next
  p = trim($1)
  if (tolower(p) == "port") next
  if (p !~ /^[0-9]+$/ || NF < 3) {
    printf "%s:%d: expected port,service,expected: %s\n", src, NR, $0 > "/dev/stderr"
    exit 1
  }
  printf "%d\t%s\t%s\n", p + 0, trim($2), trim($3)
}' "$inp/baseline.csv" > "$scratch/baseline.tsv"

# --- scan: expand ranges, last probe wins, one row per (port, proto) -----------------
: > "$scratch/rows.tsv"
awk -v basefile="$scratch/baseline.tsv" -v rowfile="$scratch/rows.tsv" \
    -v sumfile="$outdir/summary.json" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
function add(port, proto, state, svc,   k) {
  k = port SUBSEP proto
  if (k in pstate) superseded++
  pstate[k] = state
  psvc[k] = svc
  pport[k] = port
  pproto[k] = proto
}
function verdict(p, state, svc) {
  if (!(p in bsvc)) return "unbaselined"
  if (bexp[p] == "yes") {
    if (state != "open") return "unexpected"
    return (svc == bsvc[p]) ? "ok" : "wrong-service"
  }
  if (state == "open") return "should-be-closed"
  return "ok"
}
BEGIN {
  lines = 0; skipped = 0; superseded = 0
  while ((getline bl < basefile) > 0) {
    split(bl, bf, "\t")
    bsvc[bf[1] + 0] = bf[2]
    bexp[bf[1] + 0] = bf[3]
  }
  close(basefile)
}
{
  if ($0 ~ /^[ \t\r]*$/) next
  lines++
  n = split(trim($0), f, /[ \t]+/)
  if (n < 2) { skipped++; next }
  state = tolower(f[2])
  if (state != "open" && state != "closed" && state != "filtered") { skipped++; next }
  pf = f[1]
  slash = index(pf, "/")
  if (slash == 0) { skipped++; next }
  pnum = substr(pf, 1, slash - 1)
  proto = substr(pf, slash + 1)
  svc = (n >= 3) ? f[3] : ""
  dash = index(pnum, "-")
  if (dash > 0) {
    lo = substr(pnum, 1, dash - 1)
    hi = substr(pnum, dash + 1)
  } else {
    lo = pnum; hi = pnum
  }
  if (lo !~ /^[0-9]+$/ || hi !~ /^[0-9]+$/) { skipped++; next }
  for (p = lo + 0; p <= hi + 0; p++) add(p, proto, state, svc)
}
END {
  ports = 0; opened = 0; unbase = 0; attention = 0
  for (k in pstate) {
    p = pport[k]; proto = pproto[k]; state = pstate[k]; svc = psvc[k]
    v = verdict(p, state, svc)
    printf "%d\t%s\t%d,%s,%s,%s,%s\n", p, proto, p, proto, state, svc, v > rowfile
    ports++
    if (state == "open") opened++
    if (v == "unbaselined") unbase++
    if (v == "wrong-service" || v == "unexpected" || v == "should-be-closed") attention++
  }
  close(rowfile)
  summary = sprintf("{\"lines\":%d,\"ports\":%d,\"skipped\":%d,\"superseded\":%d,\"open\":%d,\"unbaselined\":%d,\"attention\":%d}", lines, ports, skipped, superseded, opened, unbase, attention)
  print summary > sumfile
  close(sumfile)
}' "$inp/scan.txt"

{
  printf 'port,proto,state,service,verdict\n'
  sort -t $'\t' -k1,1n -k2,2 "$scratch/rows.tsv" | cut -f3-
} > "$outdir/ports.csv"

echo "131-port-scan-triage: wrote $outdir/ports.csv and $outdir/summary.json"
