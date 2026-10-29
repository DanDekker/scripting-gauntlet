#!/usr/bin/env bash
# 043-sort-unique-count — normalize, sort, uniq -c, sort again.
set -euo pipefail

src="${IN:?IN not set}/app.log"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

{
  printf 'level,count\n'
  awk 'NF { print toupper($2) }' "$src" \
    | LC_ALL=C sort \
    | uniq -c \
    | awk '{ print $2 "," $1 }' \
    | LC_ALL=C sort -t, -k2,2nr -k1,1
} > "$outdir/levels.csv"

printf '{"lines":%d,"levels":%d,"top":"%s"}\n' \
  "$(awk 'NF { n++ } END { print n + 0 }' "$src")" \
  "$(awk 'NF { seen[toupper($2)] = 1 } END { print length(seen) + 0 }' "$src")" \
  "$(tail -n +2 "$outdir/levels.csv" | head -1 | cut -d, -f1)" > "$outdir/summary.json"
