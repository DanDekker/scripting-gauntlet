#!/usr/bin/env bash
# Extract the one valid JSON object/array from each reply block. Candidates are written to
# scratch files in priority order (json fence, plain fence, raw balanced span) and the
# first one jq accepts as an object/array wins.
set -euo pipefail

export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# 1. Split the transcript into one file per `=== RESPONSE <id> ===` block.
awk -v dir="$scratch" '
  BEGIN { n = 0 }
  /^=== RESPONSE [^ \t]+ ===[ \t]*$/ {
    if (n > 0) close(file)
    n++
    id = $0
    sub(/^=== RESPONSE /, "", id)
    sub(/ ===[ \t]*$/, "", id)
    print id
    file = dir "/block." n ".txt"
    printf "" > file
    next
  }
  { if (n > 0) print $0 > file }
  END { if (n > 0) close(file) }
' "$in_dir/responses.txt" > "$scratch/ids.txt"

: > "$out_dir/extracted.jsonl"
printf 'id,status,type\n' > "$out_dir/status.csv"

total=0
extracted=0
objects=0
arrays=0
index=0

while IFS= read -r id; do
  index=$((index + 1))
  total=$((total + 1))
  block="$scratch/block.$index.txt"
  cand="$scratch/cand.$index"
  mkdir -p "$cand"

  if [ -s "$block" ]; then
    # (a) ```json fences and (b) unlabelled ``` fences, in document order.
    awk -v dir="$cand" '
      function trim(s) { gsub(/^[ \t\r]+/, "", s); gsub(/[ \t\r]+$/, "", s); return s }
      function emit(   f) {
        if (info == "json") f = sprintf("%s/c.1.%03d.json", dir, seq)
        else if (info == "") f = sprintf("%s/c.2.%03d.json", dir, seq)
        else return
        printf "%s", buf > f
        close(f)
      }
      {
        line = $0
        if (infence == 0) {
          if (line ~ /^[ \t]*```/) {
            info = line
            sub(/^[ \t]*```/, "", info)
            info = tolower(trim(info))
            infence = 1; buf = ""; seq++
          }
          next
        }
        if (line ~ /^[ \t]*```[ \t]*$/) { infence = 0; emit(); next }
        buf = buf line "\n"
      }
      END { if (infence == 1) emit() }
    ' "$block"

    # (c) every balanced { } / [ ] span in the raw block, in scan order.
    awk -v dir="$cand" '
      function balanced(text, start,   i, n, c, depth, stack, in_string, escaped) {
        n = length(text)
        depth = 0; in_string = 0; escaped = 0
        for (i = start; i <= n; i++) {
          c = substr(text, i, 1)
          if (in_string) {
            if (escaped) { escaped = 0 }
            else if (c == "\\") { escaped = 1 }
            else if (c == "\"") { in_string = 0 }
            continue
          }
          if (c == "\"") { in_string = 1; continue }
          if (c == "{" || c == "[") { stack[++depth] = (c == "{" ? "}" : "]"); continue }
          if (c == "}" || c == "]") {
            if (depth == 0 || stack[depth] != c) return ""
            depth--
            if (depth == 0) return substr(text, start, i - start + 1)
          }
        }
        return ""
      }
      { text = text $0 "\n" }
      END {
        seq = 0
        n = length(text)
        for (i = 1; i <= n; i++) {
          c = substr(text, i, 1)
          if (c == "{" || c == "[") {
            span = balanced(text, i)
            if (span != "") {
              seq++
              f = sprintf("%s/c.3.%03d.json", dir, seq)
              printf "%s", span > f
              close(f)
            }
          }
        }
      }
    ' "$block"
  fi

  chosen=""
  shopt -s nullglob
  for f in "$cand"/c.1.*.json "$cand"/c.2.*.json "$cand"/c.3.*.json; do
    if jq -e 'type == "object" or type == "array"' "$f" > /dev/null 2>&1; then
      chosen="$f"
      break
    fi
  done
  shopt -u nullglob

  if [ -z "$chosen" ]; then
    printf '%s,failed,none\n' "$id" >> "$out_dir/status.csv"
    continue
  fi

  kind=$(jq -r 'type' "$chosen")
  size=$(jq -r 'if type == "object" then (keys | length) else length end' "$chosen")
  jq -c -n --arg id "$id" --arg kind "$kind" --argjson size "$size" --slurpfile doc "$chosen" \
    '{id: $id, type: $kind, keys_or_length: $size, data: $doc[0]}' >> "$out_dir/extracted.jsonl"
  printf '%s,extracted,%s\n' "$id" "$kind" >> "$out_dir/status.csv"

  extracted=$((extracted + 1))
  case "$kind" in
    object) objects=$((objects + 1)) ;;
    array) arrays=$((arrays + 1)) ;;
  esac
done < "$scratch/ids.txt"

jq -n \
  --argjson total "$total" \
  --argjson extracted "$extracted" \
  --argjson objects "$objects" \
  --argjson arrays "$arrays" \
  '{total_responses: $total, extracted_count: $extracted,
    failed_count: ($total - $extracted), objects_count: $objects, arrays_count: $arrays}' \
  > "$out_dir/summary.json"
