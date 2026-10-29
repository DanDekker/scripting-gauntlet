#!/usr/bin/env bash
# 014-logfmt — write the tokenizer once; quoted values may contain spaces.
set -euo pipefail

src="${IN:?IN not set}/app.log"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -v outdir="$outdir" '
# tokenize one logfmt record into the global arrays K[] and V[]
function tokenize(line,   i, c, len, key, val, inq, n) {
  n = 0; len = length(line); i = 1
  while (i <= len) {
    while (i <= len && substr(line, i, 1) == " ") i++
    if (i > len) break
    key = ""
    while (i <= len && substr(line, i, 1) != "=" && substr(line, i, 1) != " ") {
      key = key substr(line, i, 1); i++
    }
    if (substr(line, i, 1) != "=") break
    i++
    val = ""; inq = 0
    while (i <= len) {
      c = substr(line, i, 1)
      if (inq) {
        if (c == "\"") { inq = 0; i++ } else { val = val c; i++ }
      } else if (c == "\"") { inq = 1; i++ }
      else if (c == " ") break
      else { val = val c; i++ }
    }
    n++; K[n] = key; V[n] = val
  }
  ntok = n
  return n
}
function get(key,   j) {
  for (j = 1; j <= ntok; j++) if (K[j] == key) return V[j]
  return ""
}
{
  tokenize($0)
  path = get("path"); status = get("status"); dur = get("dur"); level = get("level")
  sub(/ms$/, "", dur)
  printf "%s,%s,%d\n", path, status, dur
  lines++
  if (level == "error") errors++
  else if (level == "warn") warns++
  else if (level == "info") infos++
}
END {
  summary = outdir "/summary.json"
  printf "{\"lines\":%d,\"errors\":%d,\"warns\":%d,\"infos\":%d}\n", lines, errors, warns, infos > summary
  close(summary)
}' "$src" | sort -t, -k3,3nr -k1,1 > "$body"

{
  printf 'path,status,dur_ms\n'
  cat "$body"
} > "$outdir/requests.csv"
