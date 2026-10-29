#!/usr/bin/env bash
# Lint a tool manifest: awk finds the duplicate keys the parser erases, jq runs the checks.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# 1. Top-level keys in raw text order. jq collapses a repeated key (last wins) before we
#    could see it, so the key list has to come out of the bytes themselves.
awk '
{
  for (i = 1; i <= length($0); i++) {
    c = substr($0, i, 1)
    if (instr) {
      if (esc) { esc = 0; continue }
      if (c == "\\") { esc = 1; continue }
      if (c == "\"") {
        instr = 0
        if (d == 1 && mode == "key") { print key; mode = "colon" }
        continue
      }
      if (d == 1 && mode == "key") key = key c
      continue
    }
    if (c == "\"") { instr = 1; if (d == 1 && mode == "key") key = ""; continue }
    if (c == "{") { d++; if (d == 1) mode = "key"; continue }
    if (c == "[") { d++; continue }
    if (c == "}") { d--; if (d == 0) exit; continue }
    if (c == "]") { d--; continue }
    if (d == 1) {
      if (c == ":" && mode == "colon") { mode = "value"; continue }
      if (c == "," && mode == "value") { mode = "key"; continue }
    }
  }
}
' "$in_dir/tools.json" > "$scratch/keys"

LC_ALL=C sort "$scratch/keys" | uniq -d > "$scratch/dups"

# 2. The structural checks, on the parsed manifest (last duplicate wins).
jq -r '
  def trim: gsub("^[ \t\r\n]+"; "") | gsub("[ \t\r\n]+$"; "");
  def asstring: if type == "string" then . else null end;
  def check($n; $d):
    ([ (if ($n | test("^[a-z0-9_]+$")) then empty else "bad-name" end),
       (if (($d.description | asstring) as $desc
            | $desc != null and (($desc | trim) | length) > 0)
        then empty else "no-description" end)
     ])
    + (if (($d.parameters | type) != "object") then ["no-parameters"]
       else
         ($d.parameters) as $p
         | (($p.properties) as $raw
            | (if (($raw | type) == "object") and (($raw | length) > 0)
               then [] else ["no-properties"] end))
           +
           (($p.properties | if type == "object" then . else {} end) as $props
            | ($p.required) as $req
            | if ($req | type) == "array" then
                (if ([$req[] as $r | select(($props | has($r)) | not)] | length) > 0
                 then ["required-not-declared"] else [] end)
              elif ($p | has("required")) then []
              elif (($props | length) > 0) then ["undeclared-required"]
              else [] end)
       end);
  . | to_entries[]
  | .key as $n
  | (.value | if type == "object" then . else {} end) as $def
  | check($n; $def)[]
  | "\($n)\t\(.)"
' "$in_dir/tools.json" > "$scratch/checks"

awk '{ printf "%s\tduplicate-key\n", $0 }' "$scratch/dups" > "$scratch/dupcodes"

{
  printf 'tool,code\n'
  cat "$scratch/checks" "$scratch/dupcodes" \
    | LC_ALL=C sort \
    | awk -F'\t' '{ printf "%s,%s\n", $1, $2 }'
} > "$out_dir/errors.csv"

tools=$(jq 'keys_unsorted | length' "$in_dir/tools.json")
errors=$(awk 'NR > 1 { c++ } END { print c + 0 }' "$out_dir/errors.csv")
invalid=$(awk -F, 'NR > 1 { print $1 }' "$out_dir/errors.csv" | LC_ALL=C sort -u | awk 'END { print NR }')

jq -n \
  --argjson tools "$tools" \
  --argjson errors "$errors" \
  --argjson invalid "$invalid" \
  '{tools: $tools, valid_tools: ($tools - $invalid), invalid_tools: $invalid, errors: $errors}' \
  > "$out_dir/summary.json"
