#!/usr/bin/env bash
# Plausible bug: uses [[ -n ${config[$q]} ]] which treats empty keys as missing
set -euo pipefail

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

declare -A config

while IFS='=' read -r key val || [[ -n "${key:-}" ]]; do
  [[ -z "${key:-}" || "$key" =~ ^# ]] && continue
  key="${key//[$'\r\n ']/}"
  config["$key"]="${val:-}"
done < "$IN/config.txt"

count_set=0
count_empty=0
count_missing=0
total_queries=0

echo "key,status,value" > "$OUT/results.csv"

while read -r q || [[ -n "${q:-}" ]]; do
  q="${q//[$'\r\n ']/}"
  [[ -z "$q" || "$q" =~ ^# ]] && continue
  total_queries=$(( total_queries + 1 ))

  # BUG: [[ -n ... ]] is false when value is empty string!
  if [[ -n "${config["$q"]:-}" ]]; then
    status="set"
    val="${config["$q"]}"
    count_set=$(( count_set + 1 ))
  else
    # Wrongly treats empty values as missing!
    status="missing"
    val=""
    count_missing=$(( count_missing + 1 ))
  fi

  echo "$q,$status,$val" >> "$OUT/results.csv"
done < "$IN/queries.txt"

printf '{"queries":%d,"set":%d,"empty":%d,"missing":%d}\n' \
  "$total_queries" "$count_set" "$count_empty" "$count_missing" > "$OUT/summary.json"
