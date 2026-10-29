#!/usr/bin/env bash
# Score eval cases with jq: one matcher per kind, unjudgeable kinds fail.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -R 'fromjson? // empty | select(type == "object")' "$in_dir/cases.jsonl" | jq -s '
  def trim: gsub("^[ \t\r\n]+"; "") | gsub("[ \t\r\n]+$"; "");
  def num: ((tostring | trim | tonumber?) // null);
  def abs: if . < 0 then -. else . end;
  map(. as $c
      | ($c.kind) as $kind
      | (($c.expected // "") | tostring | trim) as $e
      | (($c.actual // "") | tostring | trim) as $a
      | {
          id: (($c.id // "") | tostring | trim),
          kind: (($c.kind // "") | tostring | trim),
          passed: (if $kind == "exact" then ($e == $a)
                   elif $kind == "contains" then
                     (($a | ascii_downcase) | contains(($e | ascii_downcase)))
                   elif $kind == "number" then
                     (($e | num) as $left | ($a | num) as $right
                      | ($left != null and $right != null
                         and ((($left - $right) | abs) <= 0.01)))
                   else false end)
        }) as $rows
  | ($rows | length) as $total
  | ($rows | map(select(.passed)) | length) as $ok
  | {rows: $rows,
     summary: {total: $total, passed: $ok,
               failed: ($total - $ok),
               pass_rate: (if $total == 0 then 0
                           else (((($ok / $total) * 10000) | round) / 10000) end)}}
' > "$scratch/agg.json"

{
  printf 'id,kind,passed\n'
  jq -r '.rows[] | [.id, .kind, (if .passed then "true" else "false" end)] | @tsv' "$scratch/agg.json" \
    | awk -F'\t' \
        'function q(s) {
           if (index(s, ",") || index(s, "\"")) {
             gsub(/"/, "\"\"", s)
             return "\"" s "\""
           }
           return s
         }
         { printf "%s,%s,%s\n", q($1), q($2), $3 }'
} > "$out_dir/scores.csv"

jq '.summary' "$scratch/agg.json" > "$out_dir/summary.json"
