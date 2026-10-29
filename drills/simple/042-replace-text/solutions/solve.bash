#!/usr/bin/env bash
# 042-replace-text — escape the dots, replace globally, mirror the tree.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir/tree"

scanned=0
changed=0
replacements=0
: > "$outdir/changed.txt"

while IFS= read -r f; do
  rel="${f#"$indir"/}"
  mkdir -p "$outdir/tree/$(dirname "$rel")"
  sed 's/api\.example\.com/api.internal/g' "$f" > "$outdir/tree/$rel"
  n=$(awk '{ t = $0; c += gsub(/api\.example\.com/, "", t) } END { print c + 0 }' "$f")
  scanned=$((scanned + 1))
  replacements=$((replacements + n))
  if [ "$n" -gt 0 ]; then
    changed=$((changed + 1))
    printf '%s\n' "$rel" >> "$outdir/changed.txt"
  fi
done < <(find "$indir" -type f)

LC_ALL=C sort -o "$outdir/changed.txt" "$outdir/changed.txt"

printf '{"files_scanned":%d,"files_changed":%d,"replacements":%d}\n' \
  "$scanned" "$changed" "$replacements" > "$outdir/summary.json"
