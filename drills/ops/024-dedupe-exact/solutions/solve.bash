#!/usr/bin/env bash
# 024-dedupe-exact — trim into a key, keep the first hit, never sort.
set -euo pipefail

src="${IN:?IN not set}/signups.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -F',' -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { print "email,name,plan,signed_up"; next }
{
  if (trim($0) == "") next
  rows_in++
  for (i = 1; i <= 4; i++) f[i] = trim($i)
  key = f[1] SUBSEP f[2] SUBSEP f[3] SUBSEP f[4]
  if (key in seen) { dropped++; next }
  seen[key] = 1
  printf "%s,%s,%s,%s\n", f[1], f[2], f[3], f[4]
}
END {
  summary = outdir "/summary.json"
  printf "{\"rows_in\":%d,\"unique\":%d,\"dropped\":%d}\n", rows_in, rows_in - dropped, dropped > summary
  close(summary)
}' "$src" > "$outdir/deduped.csv"
