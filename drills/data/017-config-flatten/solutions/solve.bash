#!/usr/bin/env bash
# 017-config-flatten — indentation is the structure; jq renders the JSON.
set -euo pipefail

src="${IN:?IN not set}/app.yaml"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

pairs=$(mktemp)
trap 'rm -f "$pairs"' EXIT

awk '
function indent_of(s,   i) {
  for (i = 1; i <= length(s); i++) if (substr(s, i, 1) != " ") return i - 1
  return 0
}
function path_of(d,   i, p) {
  p = ""
  for (i = 1; i <= d; i++) p = (i == 1 ? keys[i] : p "." keys[i])
  return p
}
{
  s = $0
  if (s ~ /^[ \t]*$/ || s ~ /^[ \t]*#/) next
  ind = indent_of(s)
  while (depth > ind) { delete keys[depth]; depth-- }
  body = substr(s, ind + 1)

  if (body ~ /^-[ \t]/) {
    item = body; sub(/^-[ \t]+/, "", item)
    parent = path_of(depth)
    idx = lists[parent]++
    printf "%s\t%s\n", parent "." idx, item
    next
  }

  key = body; sub(/:.*/, "", key); gsub(/[ \t]+$/, "", key)
  value = body; sub(/^[^:]*:[ \t]*/, "", value)

  if (value == "") {
    depth++; keys[depth] = key
  } else {
    parent = path_of(depth)
    printf "%s\t%s\n", (parent == "" ? key : parent "." key), value
  }
}' "$src" > "$pairs"

jq -Rn 'reduce inputs as $line ({}; ($line | split("\t")) as $p | .[$p[0]] = (($p[1] | tonumber?) // $p[1]))' \
  < "$pairs" > "$outdir/flat.json"

jq '{keys: length}' "$outdir/flat.json" > "$outdir/summary.json"
