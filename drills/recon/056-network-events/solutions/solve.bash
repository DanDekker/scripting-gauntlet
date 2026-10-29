#!/usr/bin/env bash
# 056-network-events — pull a key's value out of the line, then count.
set -euo pipefail

src="${IN:?IN not set}/events.log"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -v outdir="$outdir" '
function val(line, key,   re, s) {
  re = " " key "=[^ ]*"
  if (match(line, re)) {
    s = substr(line, RSTART, RLENGTH)
    sub(/^ [^=]*=/, "", s)
    return s
  }
  return ""
}
function sort_desc(arr, count, other,   i, j, v) {
  for (i = 2; i <= count; i++) {
    v = arr[i]; j = i - 1
    while (j >= 1 && (other[arr[j]] < other[v] || (other[arr[j]] == other[v] && arr[j] > v))) {
      arr[j + 1] = arr[j]; j--
    }
    arr[j + 1] = v
  }
}
{
  action = toupper(val($0, "ACTION"))
  dpt = val($0, "DPT")
  src = val($0, "SRC")
  if (action == "" || dpt == "" || src == "") { skipped++; next }

  events++
  if (action == "ALLOW") allowed++
  else if (action == "DROP" || action == "REJECT") blocked++

  acount[action]++
  if (!(action in aname)) { aname[action] = 1; akeys[++an] = action }

  attempts[src]++
  if (!(src in sname)) { sname[src] = 1; skeys[++sn] = src }
}
END {
  sort_desc(akeys, an, acount)
  actions = outdir "/actions.csv"
  print "action,count" > actions
  for (i = 1; i <= an; i++) printf "%s,%d\n", akeys[i], acount[akeys[i]] > actions
  close(actions)

  sort_desc(skeys, sn, attempts)
  sources = outdir "/top_sources.csv"
  print "source,attempts" > sources
  for (i = 1; i <= sn && i <= 5; i++)
    printf "%s,%d\n", skeys[i], attempts[skeys[i]] > sources
  close(sources)

  summary = outdir "/summary.json"
  printf "{\"events\":%d,\"allowed\":%d,\"blocked\":%d,\"skipped\":%d}\n", events, allowed, blocked, skipped > summary
  close(summary)
}
' "$src"
