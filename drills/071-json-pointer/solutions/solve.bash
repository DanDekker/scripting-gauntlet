#!/usr/bin/env bash
# 071-json-pointer - hand jq the decoded tokens and let getpath walk them.
set -euo pipefail

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
[[ -f "$inp/doc.json" && -f "$inp/paths.txt" ]] || { echo "missing doc.json or paths.txt" >&2; exit 1; }

paths=0
found=0
{
  printf 'path,value\n'
  while IFS= read -r pointer || [[ -n "$pointer" ]]; do
    pointer="${pointer#"${pointer%%[![:space:]]*}"}"
    pointer="${pointer%"${pointer##*[![:space:]]}"}"
    [[ -z "$pointer" || "$pointer" == \#* ]] && continue
    [[ "$pointer" == /* ]] || { echo "pointer must start with /: $pointer" >&2; exit 1; }
    value=$(jq -r --arg p "$pointer" '
      def tokens: split("/") | .[1:] | map(gsub("~1"; "/") | gsub("~0"; "~"));
      . as $doc
      | ($p | tokens) as $toks
      | reduce $toks[] as $t
          ({ ok: true, v: $doc };
           if .ok == false then .
           elif (.v | type) == "array" then
             if ($t | test("^(0|[1-9][0-9]*)$")) and (($t | tonumber) < (.v | length))
             then ($t | tonumber) as $i | { ok: true, v: .v[$i] }
             else { ok: false } end
           elif (.v | type) == "object" then
             if (.v | has($t)) then { ok: true, v: .v[$t] } else { ok: false } end
           else { ok: false } end)
      | if .ok and (((.v | type) as $ty | $ty != "null" and $ty != "object" and $ty != "array"))
        then (.v | tostring) else "" end
    ' "$inp/doc.json") || { echo "cannot resolve $pointer" >&2; exit 1; }
    paths=$((paths + 1))
    [[ -n "$value" ]] && found=$((found + 1))
    printf '%s,%s\n' "$pointer" "$value"
  done < "$inp/paths.txt"
} > "$outdir/values.csv"

printf '{"paths":%d,"found":%d,"missing":%d}\n' \
  "$paths" "$found" "$((paths - found))" > "$outdir/summary.json"
