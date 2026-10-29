#!/usr/bin/env bash
# Attribute LLM spend per project and role with jq; awk only formats the decimal columns.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

export LC_ALL=C
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# pricing.csv -> TSV: drop the header, trim the cells, ignore rows that are not prices.
awk -F, '
  NR == 1 { next }
  {
    for (i = 1; i <= 3; i++) { gsub(/^[ \t\r]+/, "", $i); gsub(/[ \t\r]+$/, "", $i) }
    if (NF < 3 || $1 == "" || $2 !~ /^[0-9]+(\.[0-9]+)?$/ || $3 !~ /^[0-9]+(\.[0-9]+)?$/) next
    print $1 "\t" $2 "\t" $3
  }
' "$in_dir/pricing.csv" > "$scratch/pricing.tsv"

jq -n \
  --rawfile tsv "$scratch/pricing.tsv" \
  --rawfile sessions "$in_dir/sessions.jsonl" \
  --slurpfile budget "$in_dir/budgets.json" '
  def trim: gsub("^[ \t\r\n]+"; "") | gsub("[ \t\r\n]+$"; "");
  def clean: if type == "string" then trim else "" end;
  def nonneg: if type == "number" and . == floor and . >= 0 then . else null end;

  ($tsv | split("\n") | map(select(length > 0) | split("\t")
        | {key: .[0], value: {p: (.[1] | tonumber), c: (.[2] | tonumber)}})
      | from_entries) as $rates
  | ($budget[0]) as $budgets
  | [ $sessions | split("\n")[]
      | (try fromjson catch null)
      | select(type == "object")
      | { session: (.session_id | clean),
          project: (.project | clean),
          role: (.role | clean),
          model: (.model | clean),
          pt: (.prompt_tokens | nonneg),
          ct: (.completion_tokens | nonneg),
          success: (.success == true) } ] as $records
  | [ $records[]
      | select(.session != "" and .project != "" and .role != "" and .model != ""
               and .pt != null and .ct != null)
      | ($rates[.model]) as $rate
      | .unpriced = ($rate == null)
      | .cost = (if $rate == null then 0
                 else ((((.pt / 1000) * $rate.p) + ((.ct / 1000) * $rate.c)) * 1000000 | round) / 1000000
                 end) ] as $valid
  | ($valid | map(.cost) | add // 0) as $total
  | { total_turns: ($records | length),
      valid_turns: ($valid | length),
      unpriced_turns: ($valid | map(select(.unpriced)) | length),
      total_spend: $total,
      projects: ($valid | group_by(.project) | map(
          . as $g
          | { project: $g[0].project,
              turns: ($g | length),
              cost: (($g | map(.cost) | add) // 0),
              budget: ($budgets[$g[0].project] // null) })),
      roles: ($valid | group_by(.role) | map(
          . as $g
          | { role: $g[0].role,
              turns: ($g | length),
              cost: (($g | map(.cost) | add) // 0),
              pct_spend: (if $total == 0 then 0
                          else (((($g | map(.cost) | add) // 0) / $total * 10000 | round) / 100)
                          end) })),
      sessions: ($valid | group_by(.session) | map(all(.success))) }
  | .projects |= map(.over_budget = (if .budget == null then false else (.cost > .budget) end))
  | .total_spend = (.total_spend * 10000 | round) / 10000
' > "$scratch/agg.json"

jq -r '.projects[]
  | [.project, (.turns | tostring), (.cost | tostring),
     (if .budget == null then "" else (.budget | tostring) end),
     (if .over_budget then "true" else "false" end)]
  | @tsv' "$scratch/agg.json" \
  | awk -F'\t' '
      BEGIN { printf "project,turns,cost,budget,over_budget\n" }
      { printf "%s,%s,%.4f,%s,%s\n", $1, $2, $3 + 0,
               ($4 == "" ? "" : sprintf("%.4f", $4 + 0)), $5 }' \
  > "$out_dir/projects.csv"

jq -r '.roles[] | [.role, (.turns | tostring), (.cost | tostring), (.pct_spend | tostring)] | @tsv' \
    "$scratch/agg.json" \
  | awk -F'\t' '
      BEGIN { printf "role,turns,cost,pct_spend\n" }
      { printf "%s,%s,%.4f,%.2f\n", $1, $2, $3 + 0, $4 + 0 }' \
  > "$out_dir/roles.csv"

jq -n --slurpfile agg "$scratch/agg.json" '
  $agg[0]
  | { total_turns: .total_turns,
      valid_turns: .valid_turns,
      unpriced_turns: .unpriced_turns,
      total_spend: .total_spend,
      over_budget_projects: ([.projects[] | select(.over_budget)] | length),
      successful_sessions: ([.sessions[] | select(.)] | length),
      total_sessions: (.sessions | length) }' > "$out_dir/summary.json"
