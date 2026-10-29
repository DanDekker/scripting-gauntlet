#!/usr/bin/env bash
# Summarise an agent trace with jq: junk lines drop out as empty, then group and sum.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# fromjson? turns a bad line into empty; only objects carrying a tool survive.
jq -R 'fromjson? // empty | select(type == "object" and has("tool"))' "$in_dir/trace.jsonl" \
  | jq -s '
      map(. as $r | {
        tool: $r.tool,
        billed: (if $r.cached == true then 0 else ($r.tokens // 0) end),
        cached: (if $r.cached == true then ($r.tokens // 0) else 0 end),
        err: ($r.error != null)
      })
      | (length) as $turns
      | (map(.billed) | add // 0) as $total
      | (map(.cached) | add // 0) as $cached
      | (map(select(.err)) | length) as $errors
      | (group_by(.tool)
         | map({tool: .[0].tool,
                calls: length,
                errors: (map(select(.err)) | length),
                tokens: (map(.billed) | add // 0)})) as $tools
      | {
          tools: $tools,
          turns: $turns,
          total: $total,
          cached: $cached,
          errors: $errors,
          most: (if ($tools | length) > 0
                 then ($tools | sort_by(-.calls, .tool) | .[0].tool)
                 else "" end)
        }
    ' > "$scratch/agg.json"

{
  printf 'tool,calls,errors,tokens\n'
  jq -r '.tools[] | [.tool, .calls, .errors, .tokens] | @tsv' "$scratch/agg.json" \
    | awk -F'\t' '
        function q(s) {
          if (index(s, ",") || index(s, "\"")) {
            gsub(/"/, "\"\"", s)
            return "\"" s "\""
          }
          return s
        }
        { printf "%s,%d,%d,%d\n", q($1), $2, $3, $4 }
      '
} > "$out_dir/tools.csv"

jq '{turns: .turns, total_tokens: .total, cached_tokens: .cached,
     error_turns: .errors, most_called_tool: .most}' "$scratch/agg.json" \
  > "$out_dir/summary.json"
