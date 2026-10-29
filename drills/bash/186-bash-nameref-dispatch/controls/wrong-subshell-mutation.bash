#!/usr/bin/env bash
# Plausible bug: subshell isolation means updates in add_metric do not persist in parent scope
set -euo pipefail

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

declare -A bucket_alpha
declare -A bucket_beta
declare -A bucket_gamma

add_metric_subshell() {
  # Subshell runs in separate process: cannot mutate caller array!
  (
    local -n map=$1
    map["$2"]=$(( ${map["$2"]:-0} + $3 ))
  )
}

while read -r cat metric amount || [[ -n "${cat:-}" ]]; do
  [[ -z "${cat:-}" || "$cat" =~ ^# ]] && continue
  target_bucket="bucket_${cat}"
  add_metric_subshell "$target_bucket" "$metric" "$amount"
done < "$IN/actions.txt"

# Produces empty or zeroed totals because updates were discarded
echo "category,metric,total" > "$OUT/tallies.csv"
echo '{"categories":3,"entries":0,"total":0}' > "$OUT/summary.json"
