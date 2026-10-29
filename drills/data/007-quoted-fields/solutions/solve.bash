#!/usr/bin/env bash
# 007-quoted-fields — a real CSV parser in awk: quoted commas, escaped quotes,
# and records that span several physical lines.
set -euo pipefail

src="${IN:?IN not set}/notes.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -v outdir="$outdir" '
# does this text end inside a quoted field?
function in_quote(s,   i, c, q) {
  q = 0
  for (i = 1; i <= length(s); i++) {
    c = substr(s, i, 1)
    if (q) {
      if (c == "\"") {
        if (substr(s, i + 1, 1) == "\"") i++
        else q = 0
      }
    } else if (c == "\"") q = 1
  }
  return q
}

# parse one logical record into the global array cols; returns the field count.
# split() is deliberately not used: a field may contain a newline, and awk split()
# treats embedded newlines as field separators.
function parse(s,   pi, pc, plen, pf, pq, pn) {
  delete cols
  pn = 0; pf = ""; pq = 0; plen = length(s)
  for (pi = 1; pi <= plen; pi++) {
    pc = substr(s, pi, 1)
    if (pq) {
      if (pc == "\"") {
        if (substr(s, pi + 1, 1) == "\"") { pf = pf "\""; pi++ }
        else pq = 0
      } else pf = pf pc
    } else if (pc == "\"") pq = 1
    else if (pc == ",") { cols[++pn] = pf; pf = "" }
    else pf = pf pc
  }
  cols[++pn] = pf
  return pn
}

# quote a field for output only when it needs it
function csvq(s) {
  if (s ~ /[",\n]/) { gsub(/"/, "\"\"", s); return "\"" s "\"" }
  return s
}

{
  record = $0
  while (in_quote(record)) {
    if ((getline more) <= 0) break
    record = record "\n" more
  }

  n = parse(record)
  line = ""
  for (i = 1; i <= n; i++) {
    if (i > 1) line = line ","
    line = line csvq(cols[i])
    if (cols[i] ~ /\n/) multiline++
  }

  if (seen_header) { rows++; print line } else { seen_header = 1; print line }
}
END {
  stats = outdir "/stats.json"
  printf "{\"rows\":%d,\"multiline\":%d}\n", rows, multiline > stats
  close(stats)
}' "$src" > "$outdir/clean.csv"
