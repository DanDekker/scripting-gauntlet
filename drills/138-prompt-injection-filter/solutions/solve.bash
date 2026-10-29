#!/usr/bin/env bash
# Screen untrusted text for prompt-injection patterns with jq.
# Normalize zero-width obfuscation away first, then collect every flag that fires.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

JQ_SCREEN='
def delims: ["<|im_start|>", "<|im_end|>", "[INST]", "[/INST]", "<<SYS>>", "<</SYS>>"];
def overrides: ["ignore previous instructions", "ignore all previous instructions",
                "disregard all prior", "you are now dan", "system prompt override"];

[ .[]
  | (.text) as $raw
  | ($raw | gsub("[\u200b\u200c\u200d\ufeff]"; "")) as $norm
  | ($norm | ascii_downcase) as $low
  | ([ (if ($norm | test("(base64:|\\[base64\\])\\s*[A-Za-z0-9+/]{16,}"; "i"))
         then "base64-payload" else empty end),
       (if (any(delims[]; . as $m | $norm | contains($m)))
         then "delimiter-spoof" else empty end),
       (if ($norm | test("!\\[[^\\]]*\\]\\(https?://[^)]*\\)"; "i"))
         then "exfiltration" else empty end),
       (if (any(overrides[]; . as $p | $low | contains($p)))
         then "override" else empty end),
       (if ($raw | test("[\u200b\u200c\u200d\ufeff]"))
         then "zero-width" else empty end)
     ]) as $flags
  | {id: .id,
     source: ((.source // "") | if type == "string" then . else "" end),
     flags: $flags}
] as $rows
| ($rows | sort_by(.id)) as $sorted
| ([$rows[].flags[]] | group_by(.) | map({key: .[0], value: length}) | from_entries) as $by_flag
| {rows: $sorted,
   summary: {total_inputs: ($rows | length),
             clean_count: ([$rows[] | select(.flags == [])] | length),
             flagged_count: ([$rows[] | select((.flags | length) > 0)] | length),
             by_flag: $by_flag}}
'

jq -R 'fromjson? // empty | select(type == "object")
       | select((.id | type) == "string")
       | select((.text | type) == "string")' "$in_dir/inputs.jsonl" \
  | jq -s "$JQ_SCREEN" > "$scratch/screened.json"

{
  printf 'id,source,verdict,flags\n'
  jq -r '.rows[]
         | [ .id, .source,
             (if (.flags | length) > 0 then "flagged" else "clean" end),
             (.flags | join(";")) ]
         | join(",")' "$scratch/screened.json"
} > "$out_dir/screened.csv"

jq '.summary' "$scratch/screened.json" > "$out_dir/summary.json"
