#!/usr/bin/env bash
# Grade RAG cases with jq: retrieval, groundedness, answer relevance, then one issue.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

JQ_EVAL='
def trim: gsub("^[ \\t\\r\\n]+"; "") | gsub("[ \\t\\r\\n]+$"; "");
def str: if type == "string" then . else "" end;
def kws: if type == "array" then map(str | trim | ascii_downcase) else [] end;

[ .[]
  | (.context | str | ascii_downcase) as $ctx
  | (.answer | str | ascii_downcase) as $ans
  | (.ground_truth | str | trim | ascii_downcase) as $gt
  | (.context_keywords | kws) as $ck
  | (.answer_keywords | kws) as $ak
  | ([ $ck[] | select(. as $k | $ctx | contains($k)) ] | length) as $ck_hits
  | ([ $ak[] | select(. as $k | $ctx | contains($k)) ] | length) as $ak_hits
  | (if ($ck | length) == 0 or ($ck_hits * 2 >= ($ck | length)) then 1 else 0 end) as $cr
  | (if ($ak | length) == 0 or $ak_hits == ($ak | length) then 1 else 0 end) as $gr
  | (if ($gt | length) > 0 and ($ans | contains($gt)) then 1 else 0 end) as $ar
  | (if $cr == 0 then "bad_retrieval"
     elif $gr == 0 then "hallucination"
     elif $ar == 0 then "poor_answer"
     else "none" end) as $issue
  | {case_id: .case_id, cr: $cr, gr: $gr, ar: $ar,
     verdict: (if ($cr == 1 and $gr == 1 and $ar == 1) then "pass" else "fail" end),
     issue: $issue}
]
| sort_by(.case_id)
'

jq -R 'fromjson? // empty | select(type == "object")
       | select((.case_id | type) == "string")' "$in_dir/rag_cases.jsonl" \
  | jq -s "$JQ_EVAL" > "$scratch/eval.json"

{
  printf 'case_id,context_rel,grounded,answer_rel,verdict,issue\n'
  jq -r '.[] | [.case_id, .cr, .gr, .ar, .verdict, .issue] | map(tostring) | join(",")' \
    "$scratch/eval.json"
} > "$out_dir/eval.csv"

jq '
  length as $total
  | ([ .[] | select(.verdict == "pass") ] | length) as $passed
  | {total_cases: $total,
     passed: $passed,
     failed: ($total - $passed),
     pass_rate: (if $total == 0 then 0
                 else (((($passed / $total) * 10000) | round) / 10000) end),
     hallucinations: ([ .[] | select(.issue == "hallucination") ] | length),
     bad_retrievals: ([ .[] | select(.issue == "bad_retrieval") ] | length),
     poor_answers: ([ .[] | select(.issue == "poor_answer") ] | length)}
' "$scratch/eval.json" > "$out_dir/summary.json"
