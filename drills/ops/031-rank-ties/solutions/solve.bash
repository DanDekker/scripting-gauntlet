#!/usr/bin/env bash
# 031-rank-ties — sort once, then track the previous score while streaming.
set -euo pipefail

src="${IN:?IN not set}/scores.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F',' '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  printf "%s,%d\n", trim($1), trim($2) + 0
}' "$src" | LC_ALL=C sort -t, -k2,2nr -k1,1 | awk -F',' -v outdir="$outdir" '
{
  pos++
  if (pos == 1 || $2 != prev) { dense++; rank = pos }
  prev = $2
  if (pos == 1) top = $2
  printf "%s,%s,%d,%d\n", $1, $2, rank, dense
}
END {
  summary = outdir "/summary.json"
  printf "{\"players\":%d,\"top_score\":%d,\"distinct_scores\":%d}\n", pos, top, dense > summary
  close(summary)
}' > "$body"

{
  printf 'name,score,rank,dense_rank\n'
  cat "$body"
} > "$outdir/ranked.csv"
