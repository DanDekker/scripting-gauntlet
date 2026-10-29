#!/usr/bin/env bash
# Harvest TODO markers with awk: the prefix decides whether a TODO is a marker.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
tree="$in_dir/tree"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
: > "$scratch/rows"

while IFS= read -r path; do
  rel=${path#"$tree"/}
  awk -v file="$rel" '
    function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
    {
      line = $0
      n = length(line)
      at = 0
      for (i = 1; i <= n - 3; i++) {
        if (substr(line, i, 4) != "TODO") continue
        after = substr(line, i + 4, 1)
        if (after != "" && after ~ /[A-Za-z0-9_]/) continue
        before = (i > 1) ? substr(line, i - 1, 1) : ""
        if (before != "" && before ~ /[A-Za-z0-9_]/) continue
        pre = (i > 1) ? substr(line, 1, i - 1) : ""
        if (pre ~ /^[ \t]*$/) { at = i; break }
        head = pre
        sub(/[ \t]+$/, "", head)
        if (head != pre && head ~ /(#|\/\/|\/\*|\*|--)$/) { at = i; break }
      }
      if (at == 0) next

      rest = substr(line, at + 4)
      owner = ""
      if (substr(rest, 1, 1) == "(") {
        stop = index(rest, ")")
        if (stop > 1) {
          owner = trim(substr(rest, 2, stop - 2))
          rest = substr(rest, stop + 1)
        }
      }
      rest = trim(rest)
      if (substr(rest, 1, 1) == ":") rest = trim(substr(rest, 2))
      if (owner == "-") owner = ""
      printf "%s\t%d\tTODO\t%s\t%s\n", file, NR, owner, rest
    }
  ' "$path" >> "$scratch/rows"
done < <(find "$tree" -type f | LC_ALL=C sort)

{
  printf 'file,line,marker,owner,text\n'
  awk -F'\t' '{ printf "%s,%s,%s,%s,%s\n", $1, $2, $3, $4, $5 }' "$scratch/rows"
} > "$out_dir/todos.csv"

files=$(find "$tree" -type f | awk 'END { print NR }')
todos=$(awk 'END { print NR }' "$scratch/rows")
owners=$(awk -F'\t' '$4 != "" { print $4 }' "$scratch/rows" | LC_ALL=C sort -u | awk 'END { print NR }')
orphans=$(awk -F'\t' '$4 == "" { c++ } END { print c + 0 }' "$scratch/rows")

jq -n \
  --argjson files "$files" \
  --argjson todos "$todos" \
  --argjson owners "$owners" \
  --argjson orphans "$orphans" \
  '{files_scanned: $files, todos: $todos, owners: $owners, orphans: $orphans,
    by_marker: {"TODO": $todos}}' > "$out_dir/summary.json"
