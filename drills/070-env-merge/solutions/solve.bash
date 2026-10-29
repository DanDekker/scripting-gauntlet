#!/usr/bin/env bash
# 070-env-merge - parse both files, then let jq do the JSON quoting.
set -euo pipefail

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -v body="$body" -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
function fail(msg) { print msg > "/dev/stderr"; failed = 1; exit 1 }
FNR == 1 { file++ }
{
  line = trim($0)
  if (line == "" || substr(line, 1, 1) == "#") next
  if (substr(line, 1, 7) == "export ") line = trim(substr(line, 8))
  eq = index(line, "=")
  if (eq == 0) fail(FILENAME ":" FNR ": no =")
  key = trim(substr(line, 1, eq - 1))
  if (key !~ /^[A-Za-z_][A-Za-z0-9_]*$/) fail(FILENAME ":" FNR ": bad key " key)
  value = trim(substr(line, eq + 1))
  q = substr(value, 1, 1)
  if (q == "\"" || q == "\047") {
    rest = substr(value, 2)
    close_at = index(rest, q)
    if (close_at == 0) fail(FILENAME ":" FNR ": unterminated quote")
    value = substr(rest, 1, close_at - 1)
  } else {
    hash = index(value, "#")
    if (hash) value = trim(substr(value, 1, hash - 1))
  }
  if (!(key in firstfile)) firstfile[key] = file
  else if (firstfile[key] != file) overridden[key] = 1
  valueOf[key] = value
  keys[key] = 1
}
END {
  if (failed) exit 1
  empty = 0
  for (k in valueOf) {
    printf "%s\t%s\n", k, valueOf[k] > body
    if (valueOf[k] == "") empty++
  }
  close(body)
  printf "{\"files\":%d,\"keys\":%d,\"overridden\":%d,\"empty\":%d}\n", \
    file, length(keys), length(overridden), empty > (outdir "/summary.json")
  close(outdir "/summary.json")
}' "$inp/base.env" "$inp/local.env"

LC_ALL=C sort -t$'\t' -k1,1 "$body" \
  | jq -Rn '[inputs | split("\t") | {(.[0]): (.[1:] | join("\t"))}] | add // {}' \
  > "$outdir/config.json"
