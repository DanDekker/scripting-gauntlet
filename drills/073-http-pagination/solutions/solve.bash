#!/usr/bin/env bash
# 073-http-pagination - curl one page at a time, jq for the cursor.
set -euo pipefail

outdir="${OUT:?OUT not set}"
base="${API_BASE:?API_BASE not set}"
work="${WORK:?WORK not set}"
mkdir -p "$outdir"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

raw=$(mktemp)
dedup=$(mktemp)
trap 'rm -f "$raw" "$dedup"' EXIT

cursor=""
pages=0
while :; do
  pages=$((pages + 1))
  (( pages <= 10 )) || { echo "pagination did not terminate after 10 pages" >&2; exit 1; }
  url="$base/items"
  [[ -n "$cursor" ]] && url="$base/items?cursor=$cursor"
  code=$(curl --silent --show-error --connect-timeout 2 --max-time 5 \
    --output "$work/page.json" --write-out '%{http_code}' "$url") \
    || { echo "transport failure for $url" >&2; exit 1; }
  [[ "$code" == 200 ]] || { echo "HTTP $code from $url" >&2; exit 1; }
  jq -e '(.items | type) == "array" and ([.items[] | type] | all(. == "object"))' \
    "$work/page.json" >/dev/null \
    || { echo "items is not an array of objects in $url" >&2; exit 1; }
  jq -r '.items[] | [(.id | tostring), .name] | @tsv' "$work/page.json" >> "$raw"
  next=$(jq -r 'if .next == null then "" else (.next | if type == "string" then . else error("next is not a string") end) end' \
    "$work/page.json") || { echo "bad next cursor in $url" >&2; exit 1; }
  [[ -n "$next" ]] || break
  cursor=$next
done

awk -F'\t' '!seen[$1]++' "$raw" | LC_ALL=C sort -t$'\t' -k1,1n > "$dedup"
total=$(awk 'END { print NR }' "$raw")
unique=$(awk 'END { print NR }' "$dedup")

{
  printf 'id,name\n'
  awk -F'\t' '{ printf "%s,%s\n", $1, $2 }' "$dedup"
} > "$outdir/items.csv"

printf '{"pages":%d,"items":%d,"duplicates":%d}\n' \
  "$pages" "$unique" "$((total - unique))" > "$outdir/summary.json"
