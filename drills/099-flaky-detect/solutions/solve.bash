#!/usr/bin/env bash
# Find the flaky tests with jq: normalise passed, group by test, classify.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -R 'fromjson? // empty | select(type == "object")' "$in_dir/history.jsonl" \
  | jq -s '
  def trim: gsub("^[ \t\r\n]+"; "") | gsub("[ \t\r\n]+$"; "");
  def ispass:
    if . == true then true
    elif (type == "string") and ((. | trim | ascii_downcase) == "true") then true
    else false end;
  def rate4($fail; $total):
    ((($fail * 10000 / $total) | round) % 10000) as $frac
    | "0." + (($frac | tostring) as $s | ("0000" + $s)[-4:]);
  map(select((.test | type) == "string")
      | (.test | trim) as $name
      | select(($name | length) > 0)
      | {test: $name, passed: (.passed | ispass)})
  | . as $runs
  | (group_by(.test)
     | map({test: .[0].test,
            total: length,
            passed: (map(select(.passed)) | length),
            failed: (map(select(.passed | not)) | length)})) as $tests
  | ($tests | map(select(.passed > 0 and .failed > 0))) as $flaky
  | {rows: ($flaky | map(. + {rate: rate4(.failed; .total)})),
     summary: {tests: ($tests | length),
               flaky: ($flaky | length),
               stable_pass: ($tests | map(select(.failed == 0)) | length),
               stable_fail: ($tests | map(select(.passed == 0)) | length),
               runs: ($runs | length)}}
' > "$scratch/agg.json"

{
  printf 'test,total,passed,failed,fail_rate\n'
  jq -r '.rows[] | [.test, .total, .passed, .failed, .rate] | map(tostring) | join(",")' \
    "$scratch/agg.json"
} > "$out_dir/flaky.csv"

jq '.summary' "$scratch/agg.json" > "$out_dir/summary.json"
