#!/usr/bin/env bash
# 118-mcp-config - awk reads the raw text for duplicate keys, jq audits each server.
set -euo pipefail

in_dir="${IN:?IN not set}"
out_dir="${OUT:?OUT not set}"
mkdir -p "$out_dir"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

cfg="$in_dir/mcp.json"
envf="$in_dir/env.json"
[[ -f "$cfg" ]] || { echo "missing $cfg" >&2; exit 1; }
[[ -f "$envf" ]] || { echo "missing $envf" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# A JSON parser hides duplicate keys, so walk the raw text and print every key of the
# object that is the value of the top-level "servers" key, duplicates included.
awk '
  { text = text $0 "\n" }
  END {
    n = length(text); i = 1; depth = 0; instring = 0; esc = 0
    in_servers = 0; sdepth = 0; pending = 0; buf = ""
    while (i <= n) {
      c = substr(text, i, 1)
      if (instring) {
        if (esc) { esc = 0; i++; continue }
        if (c == "\\") { esc = 1; i++; continue }
        if (c == "\"") {
          instring = 0
          j = i + 1
          while (j <= n && substr(text, j, 1) ~ /[ \t\r\n]/) j++
          if (substr(text, j, 1) == ":") {
            if (depth == 1 && buf == "servers") pending = 1
            else if (in_servers && depth == sdepth) print buf
          }
          i++; continue
        }
        buf = buf c
        i++; continue
      }
      if (c == "\"") { instring = 1; buf = ""; i++; continue }
      if (c == "{" || c == "[") {
        if (c == "{" && pending) { in_servers = 1; sdepth = depth + 1; pending = 0 }
        depth++; i++; continue
      }
      if (c == "}" || c == "]") {
        depth--
        if (in_servers && depth < sdepth) in_servers = 0
        i++; continue
      }
      i++
    }
  }
' "$cfg" > "$scratch/names.txt"

LC_ALL=C sort "$scratch/names.txt" | uniq -d > "$scratch/dups.txt"
printf '%s' "$(jq -R -s -c 'split("\n") | map(select(length > 0))' "$scratch/dups.txt")" \
  > "$scratch/dups.json"

jq -r --argjson dups "$(cat "$scratch/dups.json")" \
      --argjson envnames "$(jq -c 'keys' "$envf")" '
  def isident: test("^[a-z0-9_-]+$");
  def trimws: gsub("^[ \t\r\n]+"; "") | gsub("[ \t\r\n]+$"; "");
  (.servers // {}) as $servers
  | [ $servers | to_entries[] | .key as $name
      | (.value | if type == "object" then . else {} end) as $s
      | ((if ($dups | index($name)) != null
            then [{p: "duplicate-name", d: "duplicate"}] else [] end)
        + (if ($name | isident) then [] else [{p: "bad-name", d: ""}] end)
        + (if (($s | has("command")) and (($s.command | type) == "string"))
             then [] else [{p: "missing-command", d: ""}] end)
        + (if ((($s | has("command")) and (($s.command | type) == "string"))
               and (($s.command | trimws) == ""))
             then [{p: "empty-command", d: ""}] else [] end)
        + (if ($s | has("args")) then
             (if (($s.args | type) != "array") then [{p: "bad-args", d: ""}]
              elif ([$s.args[] | type] | all(. == "string")) then []
              else [{p: "bad-args", d: ""}] end)
           else [] end)
        + (if ((($s.env // null) != null) and (($s.env | type) == "object")) then
             [ $s.env | keys_unsorted[] as $k
               | select(($envnames | index($k)) == null)
               | {p: "undefined-env", d: $k} ]
           else [] end)
        + ([ $s | keys_unsorted[] as $k
             | select((["command", "args", "env"] | index($k)) == null)
             | {p: "unknown-key", d: $k} ]))
        as $probs
      | {server: $name, problems: $probs} ] as $out
  | { rows: [ $out[] | .server as $sn | .problems | to_entries[]
              | [$sn, (.key | tostring), .value.p, .value.d] | @tsv ],
      summary: {
        servers: ($servers | keys | length),
        valid: ([$out[] | select((.problems | length) == 0)] | length),
        invalid: ([$out[] | select((.problems | length) > 0)] | length),
        problems: ([$out[] | .problems | length] | add) // 0
      } }
' "$cfg" > "$scratch/audit.json"

{
  printf 'server,problem,detail\n'
  jq -r '.rows[]' "$scratch/audit.json" \
    | LC_ALL=C sort -t "$(printf '\t')" -k1,1 -k2,2n \
    | awk -F'\t' '{ printf "%s,%s,%s\n", $1, $3, $4 }'
} > "$out_dir/problems.csv"

jq -c '.summary' "$scratch/audit.json" > "$out_dir/summary.json"
