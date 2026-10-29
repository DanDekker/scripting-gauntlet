#!/usr/bin/env bash
# 038-hash-dedup-tree — group by content hash, keep the shortest path, price the waste.
set -euo pipefail

tree="${IN:?IN not set}/tree"
outdir="${OUT:?OUT not set}"
[ -d "$tree" ] || { echo "no such directory: $tree" >&2; exit 1; }
mkdir -p "$outdir"

if command -v sha256sum >/dev/null 2>&1; then
  hash_of() { sha256sum "$1" | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then
  hash_of() { shasum -a 256 "$1" | cut -d' ' -f1; }
else
  echo "need sha256sum or shasum on PATH" >&2
  exit 1
fi

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
hashed="$work/hashed.tsv"
: > "$hashed"

total=0
empty=0
while IFS= read -r -d '' file; do
  total=$((total + 1))
  size=$(wc -c < "$file" | tr -d ' ')
  if [ "$size" -eq 0 ]; then
    empty=$((empty + 1))
    continue
  fi
  printf '%s\t%s\t%s\n' "$(hash_of "$file")" "${file#"$tree"/}" "$size" >> "$hashed"
done < <(find "$tree" -type f -print0)

{
  printf 'keeper,duplicate,sha256,bytes\n'
  LC_ALL=C awk -F'\t' '
  {
    h = $1; p = $2; bytes[h] = $3; members[h]++
    if (!(h in keeper) || length(p) < length(keeper[h]) \
        || (length(p) == length(keeper[h]) && p < keeper[h])) keeper[h] = p
    member[h, members[h]] = p
  }
  END {
    for (h in keeper)
      for (i = 1; i <= members[h]; i++) {
        p = member[h, i]
        if (p != keeper[h]) printf "%s,%s,%s,%s\n", keeper[h], p, h, bytes[h]
      }
  }' "$hashed" | LC_ALL=C sort
} > "$outdir/dupes.csv"

read -r unique dupes wasted < <(LC_ALL=C awk -F'\t' '
  { h = $1; bytes[h] = $3; members[h]++ }
  END {
    for (h in members) {
      unique++
      if (members[h] > 1) {
        dupes += members[h] - 1
        wasted += (members[h] - 1) * bytes[h]
      }
    }
    printf "%d %d %d\n", unique, dupes, wasted
  }' "$hashed")

printf '{"files":%d,"unique_hashes":%d,"duplicate_files":%d,"wasted_bytes":%d,"empty":%d}\n' \
  "$total" "$unique" "$dupes" "$wasted" "$empty" > "$outdir/summary.json"
