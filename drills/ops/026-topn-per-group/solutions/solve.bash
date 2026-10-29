#!/usr/bin/env bash
# 026-topn-per-group — sort the whole file once, then take the first two per group.
set -euo pipefail

src="${IN:?IN not set}/sales.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

raw=$(mktemp)
body=$(mktemp)
trap 'rm -f "$raw" "$body" "$raw.counts"' EXIT

awk -F',' '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  printf "%s,%s,%.2f\n", tolower(trim($1)), trim($2), trim($3) + 0
}' "$src" > "$raw"

rows_in=$(awk 'END { print NR + 0 }' "$raw")

LC_ALL=C sort -t, -k1,1 -k3,3nr -k2,2 "$raw" | awk -F',' -v counts="$raw.counts" '
{
  if ($1 != region) { region = $1; rank = 0; regions++ }
  rank++
  if (rank > 2) next
  rows_out++
  print $1 "," rank "," $2 "," $3
}
END {
  printf "%d %d\n", regions, rows_out > counts
  close(counts)
}' > "$body"

read -r regions rows_out < "$raw.counts"

{
  printf 'region,rank,rep,revenue\n'
  cat "$body"
} > "$outdir/top2.csv"

printf '{"regions":%d,"rows_in":%d,"rows_out":%d}\n' "$regions" "$rows_in" "$rows_out" \
  > "$outdir/summary.json"
