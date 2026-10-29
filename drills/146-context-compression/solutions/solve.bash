#!/usr/bin/env bash
# Compress a chat transcript with jq: one filter per message kind, char counts kept on
# the side so the summary can report the saving.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -R -c 'fromjson? // empty | select(type == "object")' "$in_dir/transcript.jsonl" \
  > "$scratch/records.jsonl"

jq -s '
  def text: if type == "string" then . else "" end;
  def linecount:
    if . == "" then 0
    else (split("\n") | if .[-1] == "" then length - 1 else length end) end;
  map(select(has("idx")
             and (.idx | type) == "number"
             and (.idx | floor) == .idx
             and has("role")
             and (.role | type) == "string"))
  | sort_by(.idx)
  | map(
      . as $m
      | ($m.tool | text) as $tool
      | if $m.role == "tool" then
          ($m.output | text) as $raw
          | (if $tool == "read_file"
               then "[READ: \($raw | linecount) lines, \($raw | length) chars]"
             elif $tool == "edit_file"
               then (if ($raw | contains("Successfully")) then "[EDIT: ok]" else "[EDIT: failed]" end)
             elif $tool == "bash"
               then (if ($raw | length) > 100
                     then ($raw[0:50] + "...[truncated]..." + $raw[-50:])
                     else $raw end)
             else (if ($raw | length) > 100 then ($raw[0:100] + "...") else $raw end)
             end) as $new
          | {line: {idx: $m.idx, role: $m.role, tool: $tool, output: $new},
             old: ($raw | length), new: ($new | length), is_tool: 1}
        else
          ($m.content | text) as $raw
          | {line: {idx: $m.idx, role: $m.role, content: $raw},
             old: ($raw | length), new: ($raw | length), is_tool: 0}
        end
    )
' "$scratch/records.jsonl" > "$scratch/compressed.json"

jq -c '.[] | .line' "$scratch/compressed.json" > "$out_dir/compressed.jsonl"

counts=$(jq -r '[ (map(.old) | add // 0), (map(.new) | add // 0),
                 (map(select(.is_tool == 1)) | length), length ] | @tsv' \
  "$scratch/compressed.json")

IFS=$'\t' read -r original_chars compressed_chars tool_messages total_messages <<< "$counts"

ratio=$(awk -v c="$compressed_chars" -v o="$original_chars" \
  'BEGIN { if (o == 0) print "0.0000"; else printf "%.4f\n", c / o }')

jq -n \
  --argjson total_messages "$total_messages" \
  --argjson tool_messages "$tool_messages" \
  --argjson original_chars "$original_chars" \
  --argjson compressed_chars "$compressed_chars" \
  --argjson ratio "$ratio" \
  '{total_messages: $total_messages, tool_messages: $tool_messages,
    original_chars: $original_chars, compressed_chars: $compressed_chars,
    saved_chars: ($original_chars - $compressed_chars), compression_ratio: $ratio}' \
  > "$out_dir/summary.json"
