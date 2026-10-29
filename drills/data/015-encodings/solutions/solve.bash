#!/usr/bin/env bash
# 015-encodings — sniff the bytes, decode, strip the BOM, normalise line endings.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

decode() {
  local path="$1" magic
  magic=$(head -c 3 "$path" | od -An -tx1 | tr -d ' \n')
  case "$magic" in
    efbbbf*) tail -c +4 "$path" | iconv -f UTF-8 -t UTF-8 ;;
    fffe*) iconv -f UTF-16LE -t UTF-8 "$path" ;;
    *)
      if iconv -f UTF-8 -t UTF-8 "$path" >/dev/null 2>&1; then
        iconv -f UTF-8 -t UTF-8 "$path"
      elif iconv -f UTF-16LE -t UTF-8 "$path" >/dev/null 2>&1; then
        iconv -f UTF-16LE -t UTF-8 "$path"
      else
        iconv -f ISO-8859-1 -t UTF-8 "$path"
      fi
      ;;
  esac
}

body=$(mktemp)
trap 'rm -f "$body"' EXIT

for path in "$indir"/*.csv; do
  source=$(basename "$path" .csv)
  decode "$path" | tr -d '\r' \
    | awk -F',' -v src="$source" 'NR > 1 { printf "%s,%s,%s,%s\n", $1, src, $2, $3 }' >> "$body"
done

{
  printf 'id,source,name,city\n'
  sort -t, -k1,1n "$body"
} > "$outdir/merged.csv"

files=$(find "$indir" -name '*.csv' | wc -l | tr -d ' ')
rows=$(wc -l < "$body" | tr -d ' ')
printf '{"files":%s,"rows":%s}\n' "$files" "$rows" > "$outdir/summary.json"
