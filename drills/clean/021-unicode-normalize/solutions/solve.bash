#!/usr/bin/env bash
# 021-unicode-normalize — casefold what folding means, strip what is decoration.
set -euo pipefail

src="${IN:?IN not set}/names.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

outfile="$outdir/normalised.csv"
printf 'id,key\n' > "$outfile"

tail -n +2 "$src" | while IFS=, read -r id raw; do
  [ -z "$id" ] && continue
  key=$(printf '%s' "$raw" \
    | LC_ALL=C sed -e 's/ß/ss/g' -e 's/ẞ/ss/g' \
                    -e 's/É/e/g' -e 's/é/e/g' -e 's/Á/a/g' -e 's/á/a/g' \
                    -e 's/İ/i/g' -e 's/́//g' \
    | LC_ALL=C tr 'A-Z' 'a-z' \
    | LC_ALL=C sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//')
  printf '%s,%s\n' "$id" "$key" >> "$outfile"
done

rows=$(($(wc -l < "$outfile") - 1))
distinct=$(tail -n +2 "$outfile" | cut -d, -f2- | LC_ALL=C sort -u | wc -l)
printf '{"rows":%d,"distinct":%d}\n' "$rows" "$distinct" > "$outdir/summary.json"
