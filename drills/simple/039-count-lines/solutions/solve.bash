#!/usr/bin/env bash
# 039-count-lines — awk counts records; wc -l counts newlines and undercounts.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

for f in "$indir"/*.log; do
  printf '%s,%s\n' "${f##*/}" "$(awk 'END { print NR }' "$f")" >> "$body"
done

{
  printf 'file,lines\n'
  LC_ALL=C sort "$body"
} > "$outdir/linecounts.csv"

printf '{"files":%d,"lines":%d}\n' \
  "$(awk 'END { print NR }' "$body")" \
  "$(awk -F, '{ n += $2 } END { print n + 0 }' "$body")" > "$outdir/total.json"
