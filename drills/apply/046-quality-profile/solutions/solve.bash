#!/usr/bin/env bash
# 046-quality-profile — one pass, one bucket per column, then sort the report rows.
set -euo pipefail

src="${IN:?IN not set}/customers.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

tsv=$(mktemp)
trap 'rm -f "$tsv"' EXIT

awk -F',' -v outdir="$outdir" -v tsv="$tsv" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
BEGIN {
  NULL["null"] = 1; NULL["n/a"] = 1; NULL["na"] = 1; NULL["none"] = 1; NULL["-"] = 1
}
FNR == 1 {
  width = NF
  for (i = 1; i <= width; i++) col[i] = trim($i)
  next
}
{
  if (trim($0) == "") next
  rows++
  for (i = 1; i <= width; i++) {
    v = trim($i)
    lv = tolower(v)
    if (v == "" || (lv in NULL)) { nulls[col[i]]++; continue }
    nonnull[col[i]]++
    key = col[i] SUBSEP v
    if (!(key in seen)) { seen[key] = 1; distinct[col[i]]++; order[key] = ++seq }
    freq[key]++
    if (v !~ /^-?[0-9]+(\.[0-9]+)?$/) notnum[col[i]] = 1
    if (!(col[i] in lo) || v + 0 < lo[col[i]]) lo[col[i]] = v + 0
    if (!(col[i] in hi) || v + 0 > hi[col[i]]) hi[col[i]] = v + 0
  }
}
END {
  for (i = 1; i <= width; i++) {
    c = col[i]
    best = ""; bestn = 0
    for (v in seen) {
      split(v, parts, SUBSEP)
      if (parts[1] != c) continue
      k = freq[v]
      if (k > bestn || (k == bestn && order[v] < order[c SUBSEP best])) {
        best = parts[2]; bestn = k
      }
    }
    numeric = (nonnull[c] > 0 && !(c in notnum)) ? "yes" : "no"
    if (numeric == "yes") { mn = sprintf("%.2f", lo[c]); mx = sprintf("%.2f", hi[c]) }
    else { mn = ""; mx = "" }
    total_null += nulls[c]
    if (nulls[c] > worst) { worst = nulls[c]; worstcol = c }
    printf "%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\t%d\n", c, nonnull[c], nulls[c] + 0,
      distinct[c] + 0, numeric, mn, mx, best, bestn > tsv
  }
  close(tsv)
  dst = outdir "/summary.json"
  printf "{\"rows\":%d,\"columns\":%d,\"nulls\":%d,\"worst_column\":\"%s\",\"worst_nulls\":%d}\n",
    rows, width, total_null, worstcol, worst > dst
  close(dst)
}' "$src"

{
  printf 'column,non_null,nulls,distinct,numeric,min,max,top_value,top_count\n'
  LC_ALL=C sort -k1,1 "$tsv" | tr '\t' ','
} > "$outdir/profile.csv"
