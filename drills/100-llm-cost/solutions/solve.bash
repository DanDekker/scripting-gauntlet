#!/usr/bin/env bash
# Cost a request log with jq (parse, join the rate table, round) and awk (money, totals).
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# rate table -> {"small": {"input": 0.015, "output": 0.06}, ...}
jq -R -s '
  split("\n")
  | map(gsub("\r"; "") | select(length > 0))
  | .[1:]
  | map(split(",") | map(gsub("^\\s+|\\s+$"; "")))
  | map({key: .[0], value: {input: (.[1] | tonumber), output: (.[2] | tonumber)}})
  | from_entries
' "$in_dir/pricing.csv" > "$scratch/pricing.json"

# surviving requests only: valid JSON objects with request_id, model, input_tokens
jq -R -c '
  fromjson? // empty
  | select(type == "object")
  | select(has("request_id") and has("model") and has("input_tokens"))
' "$in_dir/usage.jsonl" > "$scratch/requests.jsonl"

# one TSV line per request: status <TAB> id <TAB> model <TAB> cost
jq -r --slurpfile rates "$scratch/pricing.json" '
  ($rates[0]) as $pricing
  | (.model | tostring) as $model
  | ((.input_tokens | tonumber) / 1000) as $tin
  | (((.output_tokens // 0) | tonumber) / 1000) as $tout
  | if ($pricing | has($model) | not)
    then ["unpriced", (.request_id | tostring), $model, ""] | @tsv
    else
      ($pricing[$model].input * (if (.cached // false) == true then 0.1 else 1 end)) as $irate
      | ($pricing[$model].output) as $orate
      | ((((($tin * $irate) + ($tout * $orate)) * 1000000) | round) / 1000000) as $cost
      | ["priced", (.request_id | tostring), $model, ($cost | tostring)] | @tsv
    end
' "$scratch/requests.jsonl" > "$scratch/costs.tsv"

# priced rows: id <TAB> model <TAB> 6-decimal cost, sorted by id then model
awk -F'\t' '$1 == "priced" { printf "%s\t%s\t%.6f\n", $2, $3, $4 }' "$scratch/costs.tsv" \
  | LC_ALL=C sort -t$'\t' -k1,1 -k2,2 > "$scratch/sorted.tsv"

# per-model totals, 6-decimal money, model ascending
awk -F'\t' '$1 == "priced" { s[$3] += $4 } END { for (m in s) printf "%s\t%.6f\n", m, s[m] }' \
  "$scratch/costs.tsv" | LC_ALL=C sort -t$'\t' -k1,1 > "$scratch/models.tsv"

# counters: requests <TAB> unpriced <TAB> total
awk -F'\t' '$1 == "priced" { total += $4 } $1 == "unpriced" { unpriced++ }
  { requests++ }
  END { printf "%d\t%d\t%.6f\n", requests, unpriced, total }' "$scratch/costs.tsv" \
  > "$scratch/counters.tsv"

{
  printf 'request_id,model,cost\n'
  awk -F'\t' 'function q(s) {
      if (index(s, ",") || index(s, "\"")) {
        gsub(/"/, "\"\"", s)
        return "\"" s "\""
      }
      return s
    }
    { printf "%s,%s,%s\n", q($1), q($2), $3 }' "$scratch/sorted.tsv"
} > "$out_dir/costs.csv"

requests=$(awk -F'\t' '{ print $1 }' "$scratch/counters.tsv")
unpriced=$(awk -F'\t' '{ print $2 }' "$scratch/counters.tsv")
total=$(awk -F'\t' '{ print $3 }' "$scratch/counters.tsv")
priced=$(awk -F'\t' '$1 == "priced" { n++ } END { print n + 0 }' "$scratch/costs.tsv")
model_rows=$(awk 'END { print NR }' "$scratch/models.tsv")

{
  printf '{\n'
  printf '  "requests": %d,\n' "$requests"
  printf '  "priced": %d,\n' "$priced"
  printf '  "unpriced": %d,\n' "$unpriced"
  printf '  "total_cost": %s,\n' "$total"
  printf '  "by_model": {\n'
  if [ "$model_rows" -gt 0 ]; then
    awk -F'\t' -v n="$model_rows" '{ printf "    \"%s\": %s%s\n", $1, $2, (FNR < n ? "," : "") }' \
      "$scratch/models.tsv"
  fi
  printf '  }\n'
  printf '}\n'
} > "$out_dir/summary.json"
