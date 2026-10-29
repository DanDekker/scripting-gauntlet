#!/usr/bin/env bash
# 005-dir-hygiene — inventory, hash, dedupe, normalize, resort, manifest.
set -euo pipefail

src="${IN:?IN not set}/messy"
outdir="${OUT:?OUT not set}"
[ -d "$src" ] || { echo "no such directory: $src" >&2; exit 1; }

if command -v sha256sum >/dev/null 2>&1; then
  hash_of() { sha256sum "$1" | cut -d' ' -f1; }
else
  hash_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
: > "$work/hashed.tsv"

while IFS= read -r -d '' file; do
  rel="${file#"$src"/}"
  name="${rel##*/}"
  case "$name" in
    .DS_Store|Thumbs.db) continue ;;
    '~$'*) continue ;;
  esac
  size=$(wc -c < "$file")
  size=${size// /}
  [ "$size" -gt 0 ] || continue
  printf '%s\t%s\t%s\n' "$rel" "$size" "$(hash_of "$file")" >> "$work/hashed.tsv"
done < <(find "$src" -type f -print0 | sort -z)

mkdir -p "$outdir/clean"
printf 'original,clean,sha256,bytes\n' > "$outdir/manifest.csv"

awk -F'\t' '
function norm(base,   b) {
  b = tolower(base)
  gsub(/[ \t]+/, "-", b)
  gsub(/[^a-z0-9._-]/, "", b)
  gsub(/-+/, "-", b)
  return b
}
{
  rel = $1; size = $2; sum = $3
  # keep the shortest path per content hash, ties by lexical order
  if (!(sum in best) || length(rel) < length(best[sum]) || (length(rel) == length(best[sum]) && rel < best[sum])) {
    best[sum] = rel
    bsize[sum] = size
  }
}
END {
  for (sum in best) {
    rel = best[sum]
    n = split(rel, seg, "/")
    name = seg[n]
    if (match(name, /\.[^.]+$/)) {
      ext = tolower(substr(name, RSTART + 1))
      base = substr(name, 1, RSTART - 1)
      clean = ext "/" norm(base) "." ext
    } else {
      clean = "noext/" norm(name)
    }
    printf "%s\t%s\t%s\t%s\n", rel, clean, sum, bsize[sum]
  }
}' "$work/hashed.tsv" | sort -t$'\t' -k1,1 > "$work/plan.tsv"

while IFS=$'\t' read -r rel clean sum size; do
  mkdir -p "$outdir/clean/${clean%%/*}"
  cp "$src/$rel" "$outdir/clean/$clean"
  printf '%s,%s,%s,%s\n' "$rel" "$clean" "$sum" "$size" >> "$outdir/manifest.csv"
done < "$work/plan.tsv"
