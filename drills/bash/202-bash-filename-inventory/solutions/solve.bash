#!/usr/bin/env bash
# 202-bash-filename-inventory — walk any name with find -print0 and read -r -d ''
set -euo pipefail
export LC_ALL=C

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

tree="$IN/tree"
mkdir -p "$OUT"

files=0
total=0
spaces=0

{
  printf 'path,bytes\n'
  while IFS= read -r -d '' full; do
    rel="${full#"$tree"/}"
    size=$(wc -c < "$full" | tr -d '[:space:]')
    printf '%s,%s\n' "$rel" "$size"
    files=$(( files + 1 ))
    total=$(( total + size ))
    if [[ "$rel" == *" "* ]]; then
      spaces=$(( spaces + 1 ))
    fi
  done < <(find "$tree" -type f -print0 | sort -z)
} > "$OUT/manifest.csv"

printf '{"files":%d,"total_bytes":%d,"spaces":%d}\n' \
  "$files" "$total" "$spaces" > "$OUT/summary.json"
