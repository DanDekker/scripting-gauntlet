#!/usr/bin/env bash
# 117-i18n-keys - awk lexes the source for real calls, jq owns the locale side.
set -euo pipefail

in_dir="${IN:?IN not set}"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

src="$in_dir/src"
locale="$in_dir/locale.json"
[[ -d "$src" ]] || { echo "missing $src" >&2; exit 1; }
[[ -f "$locale" ]] || { echo "missing $locale" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

find "$src" -type f | LC_ALL=C sort > "$scratch/files.txt"

: > "$scratch/calls.tsv"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  rel=${path#"$src/"}
  awk -v rel="$rel" '
    function isspace(ch) {
      return ch == " " || ch == "\t" || ch == "\r" || ch == "\n"
    }
    { text = text $0 "\n" }
    END {
      n = length(text); i = 1; ln = 1; mode = "code"; q = ""
      while (i <= n) {
        c = substr(text, i, 1)
        if (c == "\n") { ln++; if (mode == "comment") mode = "code"; i++; continue }
        if (mode == "comment") { i++; continue }
        if (mode == "string") { if (c == q) mode = "code"; i++; continue }
        if (c == "#") { mode = "comment"; i++; continue }
        if (c == "/" && substr(text, i + 1, 1) == "/") { mode = "comment"; i += 2; continue }
        if (c == "\"" || c == "\047" || c == "`") { mode = "string"; q = c; i++; continue }
        toklen = 0
        if (substr(text, i, 6) == "i18n.t" && substr(text, i + 6, 1) == "(") toklen = 6
        else if (c == "t" && substr(text, i + 1, 1) == "(") toklen = 1
        if (toklen > 0) {
          prevc = (i > 1) ? substr(text, i - 1, 1) : ""
          if (prevc ~ /[A-Za-z0-9_$.]/) toklen = 0
        }
        if (toklen == 0) { i++; continue }
        callline = ln
        j = i + toklen + 1
        l2 = ln
        while (j <= n && isspace(substr(text, j, 1))) {
          if (substr(text, j, 1) == "\n") l2++
          j++
        }
        got = 0
        if (j <= n) {
          cj = substr(text, j, 1)
          if (cj == "\"" || cj == "\047") {
            k = j + 1; key = ""; closed = 0
            while (k <= n) {
              ck = substr(text, k, 1)
              if (ck == cj) { closed = 1; k++; break }
              if (ck == "\n") break
              key = key ck; k++
            }
            if (closed) {
              m = k; l3 = l2
              while (m <= n && isspace(substr(text, m, 1))) {
                if (substr(text, m, 1) == "\n") l3++
                m++
              }
              if (m <= n && substr(text, m, 1) == ")") got = 1
            }
          }
        }
        if (got) { printf "%s\t%d\t%s\n", rel, callline, key; i = m + 1; ln = l3 }
        else { i += toklen }
      }
    }
  ' "$path" >> "$scratch/calls.tsv"
done < "$scratch/files.txt"

jq -r 'keys[]' "$locale" | LC_ALL=C sort > "$scratch/present.txt"
cut -f3 "$scratch/calls.tsv" | LC_ALL=C sort -u > "$scratch/used.txt"

{
  printf 'file,line,key,status\n'
  awk -F'\t' -v present="$scratch/present.txt" '
    BEGIN { while ((getline line < present) > 0) if (length(line) > 0) seen[line] = 1 }
    { printf "%s,%s,%s,%s\n", $1, $2, $3, (($3 in seen) ? "present" : "missing") }
  ' "$scratch/calls.tsv"
} > "$out_dir/keys.csv"

{
  printf 'key,reason\n'
  LC_ALL=C comm -23 "$scratch/present.txt" "$scratch/used.txt" | awk '{ printf "%s,unused\n", $0 }'
} > "$out_dir/unused.csv"

files=$(awk 'END { print NR }' "$scratch/files.txt")
calls=$(awk 'END { print NR }' "$scratch/calls.tsv")
distinct=$(awk 'END { print NR }' "$scratch/used.txt")
missing=$(LC_ALL=C comm -13 "$scratch/present.txt" "$scratch/used.txt" | awk 'END { print NR }')
unused=$(LC_ALL=C comm -23 "$scratch/present.txt" "$scratch/used.txt" | awk 'END { print NR }')
invalid=$(jq -r 'to_entries[] | select(((.value|type) != "string") or .value == "") | .key' "$locale" \
  | awk 'END { print NR }')

printf '{"files":%d,"calls":%d,"distinct":%d,"missing":%d,"unused":%d,"invalid":%d}\n' \
  "$files" "$calls" "$distinct" "$missing" "$unused" "$invalid" > "$out_dir/summary.json"
