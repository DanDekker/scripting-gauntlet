#!/usr/bin/env bash
# 002-log-triage — awk, splitting on double quotes.
set -euo pipefail

src="${IN:?IN not set}/access.log"
outdir="${OUT:?OUT not set}"
[ -r "$src" ] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

awk -v outdir="$outdir" '
{
  n = split($0, q, "\"")
  if (n < 3) { skipped++; next }
  if (split(q[2], r, " ") < 3) { skipped++; next }

  s = q[3]
  gsub(/^ +| +$/, "", s)
  split(s, stat, " ")
  status = stat[1]
  if (status !~ /^[0-9][0-9][0-9]$/) { skipped++; next }

  path = r[2]
  sub(/\?.*$/, "", path)

  valid++
  sc[status]++
  pc[path]++
}
END {
  # status: count desc, then status asc (numeric)
  ns = 0
  for (code in sc) keys[++ns] = code
  for (i = 2; i <= ns; i++) {
    v = keys[i]; j = i - 1
    while (j >= 1 && (sc[keys[j]] < sc[v] || (sc[keys[j]] == sc[v] && keys[j] + 0 > v + 0))) {
      keys[j + 1] = keys[j]; j--
    }
    keys[j + 1] = v
  }
  f = outdir "/status.csv"
  printf "status,count\n" > f
  for (i = 1; i <= ns; i++) printf "%s,%d\n", keys[i], sc[keys[i]] > f
  close(f)
  split("", keys)

  # paths: hits desc, then path asc (bytes), top 5
  np = 0
  for (p in pc) paths[++np] = p
  for (i = 2; i <= np; i++) {
    v = paths[i]; j = i - 1
    while (j >= 1 && (pc[paths[j]] < pc[v] || (pc[paths[j]] == pc[v] && paths[j] > v))) {
      paths[j + 1] = paths[j]; j--
    }
    paths[j + 1] = v
  }
  g = outdir "/top_paths.csv"
  printf "path,hits\n" > g
  for (i = 1; i <= np && i <= 5; i++) printf "%s,%d\n", paths[i], pc[paths[i]] > g
  close(g)

  h = outdir "/summary.json"
  printf "{\"valid\":%d,\"skipped\":%d}\n", valid, skipped > h
  close(h)
}
' "$src"
