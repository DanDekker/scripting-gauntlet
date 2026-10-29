#!/usr/bin/env bash
# Repair tool-call arguments: jq decides validity, awk does the text surgery.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

read -r -d '' REPAIR_PROG <<'AWK' || true
function isword(ch) { return (ch != "" && ch ~ /[A-Za-z0-9_]/) }

function literals(s,   out, i, n, c, q) {
  out = ""; i = 1; n = length(s); q = ""
  while (i <= n) {
    c = substr(s, i, 1)
    if (q == "\"") {
      out = out c
      if (c == "\\" && i < n) { out = out substr(s, i + 1, 1); i += 2; continue }
      if (c == "\"") q = ""
      i++; continue
    }
    if (q == "'") {
      out = out c
      if (c == "\\" && i < n) { out = out substr(s, i + 1, 1); i += 2; continue }
      if (c == "'") q = ""
      i++; continue
    }
    if (c == "\"") { q = "\""; out = out c; i++; continue }
    if (c == "'") { q = "'"; out = out c; i++; continue }
    if (!isword(substr(s, i - 1, 1))) {
      if (substr(s, i, 5) == "False" && !isword(substr(s, i + 5, 1))) { out = out "false"; i += 5; continue }
      if (substr(s, i, 4) == "True" && !isword(substr(s, i + 4, 1))) { out = out "true"; i += 4; continue }
      if (substr(s, i, 4) == "None" && !isword(substr(s, i + 4, 1))) { out = out "null"; i += 4; continue }
    }
    out = out c; i++
  }
  return out
}

function requote(s,   out, i, n, c, ind) {
  out = ""; i = 1; n = length(s); ind = 0
  while (i <= n) {
    c = substr(s, i, 1)
    if (ind) {
      out = out c
      if (c == "\\" && i < n) { out = out substr(s, i + 1, 1); i += 2; continue }
      if (c == "\"") ind = 0
      i++; continue
    }
    if (c == "\"") { ind = 1; out = out c; i++; continue }
    if (c == "'") { out = out "\""; i++; continue }
    out = out c; i++
  }
  return out
}

function dropcommas(s,   out, i, n, c, j) {
  out = ""; i = 1; n = length(s)
  while (i <= n) {
    c = substr(s, i, 1)
    if (c == ",") {
      j = i + 1
      while (j <= n && index(" \t\r\n", substr(s, j, 1)) > 0) j++
      if (j <= n && (substr(s, j, 1) == "}" || substr(s, j, 1) == "]")) { i++; continue }
    }
    out = out c; i++
  }
  return out
}

{
  s = $0
  sub(/^[ \t\r]+/, "", s)
  sub(/[ \t\r]+$/, "", s)
  if (substr(s, 1, 1) != "{" && substr(s, 1, 1) != "[") s = "{" s "}"
  s = literals(s)
  s = requote(s)
  s = dropcommas(s)
  printf "%s", s
}
AWK

# Normalised compact JSON with recursively sorted keys, or non-zero exit.
normalize() {
  printf '%s' "$1" | jq -ce '
    def ssort: if type == "object"
                then (to_entries | map({key: .key, value: (.value | ssort)}) | sort_by(.key) | from_entries)
                elif type == "array" then map(ssort)
                else . end;
    select(type == "object" or type == "array") | ssort' 2>/dev/null
}

calls=$(jq -R -r '
  fromjson? | select(type == "object")
  | select(has("call_id") and has("name") and has("raw_args"))
  | [(.call_id | tostring), (.name | tostring), (.raw_args | tostring)] | @tsv
' "$in_dir/calls.jsonl")

rows=()
dump=()
valid=0
repaired=0
unfixable=0

while IFS=$'\t' read -r call_id name raw; do
  [ -n "$call_id" ] || continue
  if args=$(normalize "$raw"); then
    status="valid"
    valid=$((valid + 1))
  else
    fixed=$(printf '%s\n' "$raw" | awk "$REPAIR_PROG")
    if args=$(normalize "$fixed"); then
      status="repaired"
      repaired=$((repaired + 1))
    else
      status="unfixable"
      unfixable=$((unfixable + 1))
    fi
  fi
  rows+=("$call_id,$name,$status")
  if [ "$status" != "unfixable" ]; then
    dump+=("$(jq -cn --arg call_id "$call_id" --arg name "$name" --arg status "$status" \
      --argjson args "$args" '{call_id: $call_id, name: $name, status: $status, args: $args}')")
  fi
done <<< "$calls"

{
  printf 'call_id,name,status\n'
  for row in "${rows[@]}"; do printf '%s\n' "$row"; done
} > "$out_dir/report.csv"

{
  for line in "${dump[@]}"; do printf '%s\n' "$line"; done
} > "$out_dir/repaired.jsonl"

jq -n \
  --argjson total_calls "${#rows[@]}" \
  --argjson valid_count "$valid" \
  --argjson repaired_count "$repaired" \
  --argjson unfixable_count "$unfixable" \
  '{total_calls: $total_calls, valid_count: $valid_count,
    repaired_count: $repaired_count, unfixable_count: $unfixable_count}' > "$out_dir/summary.json"
