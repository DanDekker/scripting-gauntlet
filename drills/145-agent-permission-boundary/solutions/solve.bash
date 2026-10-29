#!/usr/bin/env bash
# Audit tool invocations against a capability policy. jq does the per-invocation rule
# check (it already speaks JSON), the shell only formats.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# Blank lines, bad JSON and non-objects all fall out here.
jq -R -c 'fromjson? // empty | select(type == "object")' "$in_dir/trace.jsonl" \
  > "$scratch/records.jsonl"

jq -s --slurpfile policy "$in_dir/policy.json" '
  ($policy[0]) as $p
  | ($p.allowed_tools // []) as $allowed
  | ($p.allowed_domains // []) as $domains
  | ($p.banned_commands // []) as $banned
  | map(select(has("id") and (.id | type) == "string" and (.id | length) > 0))
  | map(
      . as $r
      | (if (.tool | type) == "string" then .tool else "" end) as $tool
      | (if (.args | type) == "object" then .args else {} end) as $args
      | (if ($args.cmd | type) == "string" then $args.cmd else "" end) as $cmd
      | (if ($args.url | type) == "string" then $args.url else "" end) as $url
      | (if ($args.path | type) == "string" then $args.path else "" end) as $path
      | (($url | split("://")) as $bits
         | if ($bits | length) > 1
           then ($bits[1] | split("/")[0] | split("@") | last | split(":")[0] | ascii_downcase)
           else "" end) as $host
      | [ (if $tool == "bash"
             and any($banned[]; . as $b | $cmd | contains($b))
           then "banned-command" else empty end),
          (if $tool == "http_get" and ($domains | index($host) | not)
           then "disallowed-domain" else empty end),
          (if (($path | startswith("/")) or any($path | split("/")[]; . == ".."))
           then "path-traversal" else empty end),
          (if ($allowed | index($tool) | not) then "unknown-tool" else empty end)
        ] as $violations
      | {id: $r.id,
         tool: $tool,
         verdict: (if ($violations | length) == 0 then "allowed" else "denied" end),
         violations: ($violations | sort | join(";")),
         count: ($violations | length)}
    )
  | sort_by(.id)
' "$scratch/records.jsonl" > "$scratch/audit.json"

{
  printf 'id,tool,verdict,violations\n'
  jq -r '.[] | [.id, .tool, .verdict, .violations] | @tsv' "$scratch/audit.json" \
    | awk -F'\t' '{ printf "%s,%s,%s,%s\n", $1, $2, $3, $4 }'
} > "$out_dir/audit.csv"

jq '{
  total_invocations: length,
  allowed_count: (map(select(.verdict == "allowed")) | length),
  denied_count: (map(select(.verdict == "denied")) | length),
  violations_count: (map(.count) | add // 0)
}' "$scratch/audit.json" > "$out_dir/summary.json"
