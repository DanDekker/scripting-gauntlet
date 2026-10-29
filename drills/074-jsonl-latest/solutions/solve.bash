#!/usr/bin/env bash
# 074-jsonl-latest - jq normalises each line, awk keeps the newest per id.
set -euo pipefail

src="${IN:?IN not set}/events.jsonl"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
[[ -f "$src" ]] || { echo "missing $src" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

raw=$(mktemp)
dedup=$(mktemp)
trap 'rm -f "$raw" "$dedup"' EXIT

jq -R -r '
  select((gsub("^[ \t\r]+|[ \t\r]+$"; "") | length) > 0)
  | fromjson
  | if type == "object"
       and (.id | type) == "string"
       and (.ts | type) == "string"
       and (.status | type) == "string"
    then [.id, .ts, .status] | @tsv
    else error("record missing string id, ts or status") end
' < "$src" > "$raw"

awk -F'\t' '
{ records++ }
!(($1) in best) || ($2 >= bestts[$1]) { bestts[$1] = $2; best[$1] = $3 }
END {
  for (k in best) printf "%s\t%s\t%s\n", k, bestts[k], best[k]
}' "$raw" | LC_ALL=C sort -t$'\t' -k1,1 > "$dedup"

{
  printf 'id,ts,status\n'
  awk -F'\t' '{ printf "%s,%s,%s\n", $1, $2, $3 }' "$dedup"
} > "$outdir/latest.csv"

records=$(awk 'END { print NR }' "$raw")
ids=$(awk 'END { print NR }' "$dedup")
printf '{"records":%d,"ids":%d,"dropped":%d}\n' \
  "$records" "$ids" "$((records - ids))" > "$outdir/summary.json"
