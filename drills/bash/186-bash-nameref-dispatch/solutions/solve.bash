#!/usr/bin/env bash
# 186-bash-nameref-dispatch — dispatch tallies in-place using bash namerefs.
set -euo pipefail

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

# Associative arrays for categories
declare -A bucket_alpha
declare -A bucket_beta
declare -A bucket_gamma

# Nameref helper: prefixed parameter name avoids caller-scope collisions
add_metric_tally() {
  local -n __dest_map=$1
  local __metric=$2
  local __delta=$3
  __dest_map["$__metric"]=$(( ${__dest_map["$__metric"]:-0} + __delta ))
}

while read -r cat metric amount || [[ -n "${cat:-}" ]]; do
  [[ -z "${cat:-}" || "$cat" =~ ^# ]] && continue
  target_bucket="bucket_${cat}"
  add_metric_tally "$target_bucket" "$metric" "$amount"
done < "$IN/actions.txt"

# Collect and sort output
categories=("alpha" "beta" "gamma")
total_sum=0
total_entries=0

tmp_csv=$(mktemp)
echo "category,metric,total" > "$OUT/tallies.csv"

for c in "${categories[@]}"; do
  bucket_name="bucket_${c}"
  local_read() {
    local -n __read_map=$1
    local __c=$2
    for m in "${!__read_map[@]}"; do
      val="${__read_map[$m]}"
      echo "$__c,$m,$val" >> "$tmp_csv"
      total_sum=$(( total_sum + val ))
      total_entries=$(( total_entries + 1 ))
    done
  }
  local_read "$bucket_name" "$c"
done

# Sort entries deterministically: category then metric
sort -t',' -k1,1 -k2,2 "$tmp_csv" >> "$OUT/tallies.csv"
rm -f "$tmp_csv"

printf '{"categories":%d,"entries":%d,"total":%d}\n' \
  "${#categories[@]}" "$total_entries" "$total_sum" > "$OUT/summary.json"
