#!/usr/bin/env bash
# 041-find-largest — size the leaves, then one sort with an explicit tie-break.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

find "$indir" -type f | while IFS= read -r f; do
  rel="${f#"$indir"/}"
  printf '%s,%s\n' "$rel" "$(wc -c < "$f" | tr -d '[:space:]')"
done > "$body"

{
  printf 'path,bytes\n'
  LC_ALL=C sort -t, -k2,2nr -k1,1 "$body"
} > "$outdir/sizes.csv"

printf '{"files":%d,"bytes":%d,"largest":"%s"}\n' \
  "$(awk 'END { print NR }' "$body")" \
  "$(awk -F, '{ n += $2 } END { print n + 0 }' "$body")" \
  "$(LC_ALL=C sort -t, -k2,2nr -k1,1 "$body" | head -1 | cut -d, -f1)" > "$outdir/largest.json"
