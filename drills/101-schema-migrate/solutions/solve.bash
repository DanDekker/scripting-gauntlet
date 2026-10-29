#!/usr/bin/env bash
# Diff two schemas with jq: one row per (property, code), then the breaking/safe counts.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

rows=$(jq -n -r --slurpfile old "$in_dir/old_schema.json" --slurpfile new "$in_dir/new_schema.json" '
  def props: (.properties // {});
  def kind: if type == "object" then (.type // "") else "" end;
  ($old[0]) as $o
  | ($new[0]) as $n
  | ($o | props) as $op
  | ($n | props) as $np
  | [($o.required // [])[] | select(. as $r | $op | has($r))] as $oreq
  | [($n.required // [])[] | select(. as $r | $np | has($r))] as $nreq
  | (($op | keys) + ($np | keys) | unique) as $names
  | [ $names[] as $name
      | if ($np | has($name) | not) then {property: $name, code: "removed"}
        elif ($op | has($name) | not) then {property: $name, code: "added"}
        else
          (if (($op[$name] | kind) != ($np[$name] | kind))
             then {property: $name, code: "type-changed"} else empty end),
          (if (($nreq | index($name)) != null) and (($oreq | index($name)) == null)
             then {property: $name, code: "now-required"} else empty end),
          (if (($oreq | index($name)) != null) and (($nreq | index($name)) == null)
             then {property: $name, code: "now-optional"} else empty end)
        end
    ]
  | sort_by([.property, .code])
  | .[]
  | [.property, .code]
  | @tsv
')

{
  printf 'property,code\n'
  printf '%s\n' "$rows" | awk -F'\t' 'NF == 2 { printf "%s,%s\n", $1, $2 }'
} > "$out_dir/changes.csv"

breaking=$(printf '%s\n' "$rows" | awk -F'\t' \
  '$2 == "removed" || $2 == "type-changed" || $2 == "now-required" { n++ } END { print n + 0 }')
safe=$(printf '%s\n' "$rows" | awk -F'\t' \
  '$2 == "added" || $2 == "now-optional" { n++ } END { print n + 0 }')
properties=$(printf '%s\n' "$rows" | awk -F'\t' 'NF == 2 { print $1 }' | LC_ALL=C sort -u | awk 'END { print NR }')

jq -n --argjson breaking "$breaking" --argjson safe "$safe" --argjson properties "$properties" \
  '{breaking: $breaking, safe: $safe, properties: $properties}' > "$out_dir/summary.json"
