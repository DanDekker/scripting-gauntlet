#!/usr/bin/env bash
# Fold observations into a memory store: jq normalises, awk applies expiry + conflict
# resolution, sort decides eviction order deterministically.
set -euo pipefail

in_dir="${IN:?IN not set}"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
[[ -f $in_dir/memory.jsonl ]] || { echo "missing $in_dir/memory.jsonl" >&2; exit 1; }
[[ -f $in_dir/config.json ]] || { echo "missing $in_dir/config.json" >&2; exit 1; }

max_entries=$(jq -er '.max_entries | numbers' "$in_dir/config.json") \
  || { echo "config.json: max_entries must be a number" >&2; exit 1; }
as_of=$(jq -er '.as_of | numbers' "$in_dir/config.json") \
  || { echo "config.json: as_of must be a number" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -R -r '
  (fromjson? // empty)
  | select(type == "object")
  | select((.key | type) == "string" and (.key | length) > 0)
  | [ .key,
      ((.value // "") | tostring),
      (if ((.ts | type) == "number") then (.ts | tostring) else "0" end),
      (if ((.ttl | type) == "number") then (.ttl | tostring) else "-" end) ]
  | @tsv
' < "$in_dir/memory.jsonl" > "$scratch/records.tsv"

awk -F'\t' -v as_of="$as_of" -v counts="$scratch/counts" '
  {
    observations++
    if ($4 != "-" && ($3 + $4) <= as_of) { expired++; next }
    if ($1 in best_ts) {
      conflicts++
      if (($3 + 0) >= best_ts[$1]) { best_ts[$1] = $3 + 0; best_val[$1] = $2 }
    } else {
      best_ts[$1] = $3 + 0
      best_val[$1] = $2
    }
  }
  END {
    for (key in best_ts) printf "%s\t%s\t%d\n", key, best_val[key], best_ts[key]
    printf "%d\t%d\t%d\n", observations, expired, conflicts > counts
  }
' "$scratch/records.tsv" > "$scratch/winners.tsv"

# Eviction order: oldest first, and among equal timestamps the key that sorts last.
LC_ALL=C sort -t$'\t' -k3,3n -k1,1r "$scratch/winners.tsv" > "$scratch/evict.tsv"
total=$(wc -l < "$scratch/evict.tsv" | tr -d ' ')
drop=$(( total > max_entries ? total - max_entries : 0 ))
tail -n "+$((drop + 1))" "$scratch/evict.tsv" | LC_ALL=C sort -t$'\t' -k3,3nr -k1,1 \
  > "$scratch/store.tsv"

{
  printf 'key,value,ts\n'
  awk -F'\t' '{ printf "%s,%s,%s\n", $1, $2, $3 }' "$scratch/store.tsv"
} > "$out_dir/memory.csv"

IFS=$'\t' read -r observations expired conflicts < "$scratch/counts"
stored=$(wc -l < "$scratch/store.tsv" | tr -d ' ')
keys=$(cut -f1 "$scratch/store.tsv" | LC_ALL=C sort | awk 'BEGIN { printf "[" } { printf "%s\"%s\"", (NR > 1 ? "," : ""), $0 } END { printf "]" }')

printf '{"observations":%d,"expired":%d,"conflicts":%d,"stored":%d,"evicted":%d,"keys":%s}\n' \
  "$observations" "$expired" "$conflicts" "$stored" "$drop" "$keys" > "$out_dir/summary.json"
