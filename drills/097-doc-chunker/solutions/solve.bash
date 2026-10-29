#!/usr/bin/env bash
# Chunk markdown docs with awk: sections, then paragraphs, then a text-keyed dedupe.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
docs_dir="$in_dir/docs"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
: > "$scratch/records"
: > "$scratch/empty"

while IFS= read -r path; do
  rel=${path##*/}
  awk -v doc="$rel" -v out="$scratch/records" -v emptyfile="$scratch/empty" '
    # One paragraph slot is emitted per flush, empty ones counted but not emitted.
    function flush(   i, text, key, tokens, parts, line) {
      if (nlines == 0) return
      text = ""
      for (i = 1; i <= nlines; i++) {
        line = buf[i]
        sub(/[ \t\r]+$/, "", line)
        text = (i == 1) ? line : text "\n" line
      }
      sub(/^[ \t\r\n]+/, "", text)
      sub(/[ \t\r\n]+$/, "", text)
      idx++
      nlines = 0
      if (text == "") { empty++; return }
      tokens = split(text, parts, /[ \t\r\n]+/)
      key = text
      gsub(/\n/, "\001", key)
      printf "%s\t%s\t%d\t%d\t%d\t%s\n", doc, section, idx, tokens, length(text), key >> out
    }
    BEGIN { section = "(preamble)"; idx = 0; nlines = 0; empty = 0 }
    {
      if (substr($0, 1, 2) == "# ") {
        flush()
        section = substr($0, 3)
        sub(/[ \t\r]+$/, "", section)
        sub(/^[ \t]+/, "", section)
        next
      }
      if ($0 == "" || $0 == "\r") { flush(); next }
      buf[++nlines] = $0
    }
    END { flush(); print empty >> emptyfile }
  ' "$path"
done < <(find "$docs_dir" -maxdepth 1 -type f -name '*.md' | LC_ALL=C sort)

# Keep the first occurrence of each trimmed text; records already arrive in output order.
awk -F'\t' -v dupfile="$scratch/dups" '
  {
    if ($6 in seen) { dup++; next }
    seen[$6] = 1
    keep[++k] = $0
  }
  END {
    printf "id,doc,section,tokens,chars\n"
    for (i = 1; i <= k; i++) {
      split(keep[i], f, "\t")
      printf "%s#%s#%d,%s,%s,%d,%d\n", f[1], f[2], f[3], f[1], f[2], f[4], f[5]
    }
    print dup + 0 > dupfile
  }
' "$scratch/records" > "$out_dir/chunks.csv"

documents=$(find "$docs_dir" -maxdepth 1 -type f -name '*.md' | awk 'END { print NR }')
chunks=$(awk 'NR > 1 { c++ } END { print c + 0 }' "$out_dir/chunks.csv")
tokens=$(awk -F, 'NR > 1 { t += $4 } END { print t + 0 }' "$out_dir/chunks.csv")
empty=$(awk '{ s += $1 } END { print s + 0 }' "$scratch/empty")
duplicates=$(cat "$scratch/dups")

jq -n \
  --argjson documents "$documents" \
  --argjson chunks "$chunks" \
  --argjson duplicates "$duplicates" \
  --argjson empty "$empty" \
  --argjson tokens "$tokens" \
  '{documents: $documents, total_chunks: $chunks, duplicates_dropped: $duplicates,
    empty_dropped: $empty, tokens: $tokens}' > "$out_dir/summary.json"
