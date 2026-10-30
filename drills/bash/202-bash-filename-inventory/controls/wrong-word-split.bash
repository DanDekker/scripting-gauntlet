#!/usr/bin/env bash
# Plausible bug: walks the tree with an unquoted command substitution, so every
# name containing a space is split into two bogus names.
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
  # BUG: unquoted $(...) word-splits on spaces and glob-expands.
  for full in $(find "$tree" -type f); do
    rel="${full#"$tree"/}"
    if [[ ! -f "$full" ]]; then
      size=0
    else
      size=$(wc -c < "$full" | tr -d '[:space:]')
    fi
    printf '%s,%s\n' "$rel" "$size"
    files=$(( files + 1 ))
    total=$(( total + size ))
    if [[ "$rel" == *" "* ]]; then
      spaces=$(( spaces + 1 ))
    fi
  done
} > "$OUT/manifest.csv"

printf '{"files":%d,"total_bytes":%d,"spaces":%d}\n' \
  "$files" "$total" "$spaces" > "$OUT/summary.json"
