#!/usr/bin/env bash
# 088-content-hint - normalise the query once, then let awk scan each candidate file.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
notes="$inp/notes"
mkdir -p "$outdir"
[[ -r "$inp/query.txt" ]] || { echo "missing query.txt" >&2; exit 1; }

query=$(tr '[:upper:]' '[:lower:]' < "$inp/query.txt" | tr -s ' \t\n' ' ' | sed 's/^ //; s/ $//')
[[ -n "$query" ]] || { echo "query.txt is empty" >&2; exit 1; }

rows=$(mktemp)
trap 'rm -f "$rows"' EXIT

files_scanned=0
skipped_large=0
matching_lines=0
matching_files=0

while IFS= read -r -d '' file; do
  files_scanned=$((files_scanned + 1))
  size=$(wc -c < "$file" | tr -d ' ')
  if (( size > 1048576 )); then
    skipped_large=$((skipped_large + 1))
    continue
  fi
  hits=$(awk -v q="$query" '
    {
      line = $0
      low = tolower(line)
      gsub(/[ \t]+/, " ", low)
      sub(/^ /, "", low); sub(/ $/, "", low)
      if (index(low, q)) {
        gsub(/^[ \t]+|[ \t]+$/, "", line)
        printf "%d\t%s\n", FNR, line
      }
    }' "$file")
  [[ -z "$hits" ]] && continue
  matching_files=$((matching_files + 1))
  while IFS= read -r hit; do
    matching_lines=$((matching_lines + 1))
    printf '%s\t%s\n' "${file#"$notes/"}" "$hit" >> "$rows"
  done <<< "$hits"
done < <(find "$notes" -type f \
  \( -name '*.md' -o -name '*.txt' -o -name '*.log' \) ! -path '*/.*' -print0)

LC_ALL=C sort -t$'\t' -k1,1 -k2,2n "$rows" > "$rows.sorted"
trap 'rm -f "$rows" "$rows.sorted"' EXIT

{
  printf 'path,line,text\n'
  awk -F'\t' '{ printf "%s,%s,%s\n", $1, $2, $3 }' "$rows.sorted"
} > "$outdir/matches.csv"

if [[ -s "$rows.sorted" ]]; then
  first=$(head -1 "$rows.sorted")
  IFS=$'\t' read -r fpath fline ftext <<< "$first"
  printf '{"path":"%s","line":%s,"text":"%s"}\n' "$fpath" "$fline" "$ftext" \
    > "$outdir/match.json"
fi

printf '{"files_scanned":%d,"matching_files":%d,"matching_lines":%d,"skipped_large":%d}\n' \
  "$files_scanned" "$matching_files" "$matching_lines" "$skipped_large" \
  > "$outdir/summary.json"
