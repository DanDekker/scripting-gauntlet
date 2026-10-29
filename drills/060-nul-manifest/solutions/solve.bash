#!/usr/bin/env bash
set -euo pipefail

tree="${IN:?IN not set}/tree"
out="${OUT:?OUT not set}"
work="${WORK:?WORK not set}/manifest.jsonl"
files0="$WORK/files0"
[[ -d "$tree" ]] || { echo "missing tree: $tree" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

if command -v sha256sum >/dev/null; then
  hash_of() { sha256sum < "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null; then
  hash_of() { shasum -a 256 < "$1" | cut -d' ' -f1; }
else
  echo "need sha256sum or shasum" >&2
  exit 1
fi

: > "$work"
find "$tree" -type f -print0 > "$files0"
files=0
bytes=0
empty=0
while IFS= read -r -d '' file; do
  size=$(wc -c < "$file" | tr -d ' ') || { echo "cannot read: $file" >&2; exit 1; }
  hash=$(hash_of "$file") || { echo "cannot hash: $file" >&2; exit 1; }
  rel=${file#"$tree"/}
  jq -cn --arg path "$rel" --argjson bytes "$size" --arg sha256 "$hash" \
    '{path:$path,bytes:$bytes,sha256:$sha256}' >> "$work"
  files=$((files + 1))
  bytes=$((bytes + size))
  if [[ "$size" -eq 0 ]]; then empty=$((empty + 1)); fi
done < "$files0"

jq -s 'sort_by(.path)' "$work" > "$out/manifest.json"
printf '{"files":%d,"bytes":%d,"empty":%d}\n' "$files" "$bytes" "$empty" > "$out/summary.json"
