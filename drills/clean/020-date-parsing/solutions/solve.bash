#!/usr/bin/env bash
# 020-date-parsing — one month table, one validity check, no date(1).
set -euo pipefail

src="${IN:?IN not set}/dates.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function days(y, m) {
  if (m == 2) return ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) ? 29 : 28
  if (m == 4 || m == 6 || m == 9 || m == 11) return 30
  return 31
}
function iso(y, m, d) {
  if (m < 1 || m > 12 || d < 1 || d > days(y, m)) return ""
  return sprintf("%04d-%02d-%02d", y, m, d)
}
function parse(raw,   s, w, n) {
  s = trim(raw)
  if (s ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T/)
    return iso(substr(s, 1, 4) + 0, substr(s, 6, 2) + 0, substr(s, 9, 2) + 0)
  if (s ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/)
    return iso(substr(s, 1, 4) + 0, substr(s, 6, 2) + 0, substr(s, 9, 2) + 0)
  if (s ~ /^[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]$/)
    return iso(substr(s, 7, 4) + 0, substr(s, 1, 2) + 0, substr(s, 4, 2) + 0)
  if (s ~ /^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$/)
    return iso(substr(s, 1, 4) + 0, substr(s, 5, 2) + 0, substr(s, 7, 2) + 0)
  n = split(s, w, " ")
  if (n == 3) {
    if (w[1] ~ /^[0-9]+$/ && w[3] ~ /^[0-9][0-9][0-9][0-9]$/ && (tolower(w[2]) in MONTH))
      return iso(w[3] + 0, MONTH[tolower(w[2])], w[1] + 0)
    if (w[2] ~ /^[0-9]+$/ && w[3] ~ /^[0-9][0-9][0-9][0-9]$/ && (tolower(w[1]) in MONTH))
      return iso(w[3] + 0, MONTH[tolower(w[1])], w[2] + 0)
  }
  return ""
}
BEGIN {
  split("january february march april may june july august september october november december", A, " ")
  split("jan feb mar apr may jun jul aug sep oct nov dec", B, " ")
  for (i = 1; i <= 12; i++) { MONTH[A[i]] = i; MONTH[B[i]] = i }
}
NR == 1 { print "id,date"; next }
{
  if (trim($0) == "") next
  d = parse($2)
  rows++
  if (d == "") failed++
  else {
    parsed++
    if (first == "" || d < first) first = d
    if (last == "" || d > last) last = d
  }
  printf "%s,%s\n", trim($1), d
}
END {
  summary = outdir "/summary.json"
  printf "{\"rows\":%d,\"parsed\":%d,\"failed\":%d,\"earliest\":\"%s\",\"latest\":\"%s\"}\n", rows, parsed, failed, first, last > summary
  close(summary)
}' "$src" > "$outdir/normalised.csv"
