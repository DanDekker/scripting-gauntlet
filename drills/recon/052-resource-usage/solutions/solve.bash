#!/usr/bin/env bash
# 052-resource-usage — longest-prefix mount match, then one JSON line.
set -euo pipefail

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
path="/var/lib/app/queue.db"
for f in df-k.txt uptime.txt cpucount.txt; do
  [ -r "$inp/$f" ] || { echo "cannot read $inp/$f" >&2; exit 1; }
done
mkdir -p "$outdir"

load1=$(awk '
/load averages:/ {
  for (i = 1; i <= NF; i++) if ($i == "averages:") { v = $(i + 1); sub(/,/, "", v); print v + 0; exit }
}' "$inp/uptime.txt")
cpus=$(awk 'NR == 1 { print $1 + 0; exit }' "$inp/cpucount.txt")
[ -n "$load1" ] || { echo "no load averages in uptime.txt" >&2; exit 1; }
[ -n "$cpus" ] || { echo "no cpu count in cpucount.txt" >&2; exit 1; }

json=$(awk -v path="$path" -v load1="$load1" -v cpus="$cpus" '
NR == 1 { next }
NF < 6  { next }
{
  mp = $6
  for (i = 7; i <= NF; i++) mp = mp " " $i
  pct = $5
  sub(/%$/, "", pct)
  n++
  MP[n] = mp
  PCT[n] = pct + 0
  AVAIL[n] = $4 + 0
}
END {
  bestlen = -1
  for (i = 1; i <= n; i++) {
    if (!contains(MP[i], path)) continue
    if (length(MP[i]) > bestlen) { bestlen = length(MP[i]); best = MP[i]; bpct = PCT[i]; bavail = AVAIL[i] }
  }
  if (bestlen < 0) {
    printf "{\"mount\":\"\"}\n"
    exit
  }
  printf "{\"path\":\"%s\",\"mount\":\"%s\",\"used_pct\":%d,\"available_kb\":%d,\"load1\":%.2f,\"cpus\":%d,\"load_per_cpu\":%.2f,\"warning\":%s,\"mounts\":%d}\n", \
    path, best, bpct, bavail, load1 + 0, cpus + 0, (load1 + 0) / (cpus + 0), (bpct >= 90 ? "true" : "false"), n
}
function contains(mp, p) {
  if (mp == "") return 0
  if (p == mp) return 1
  if (mp == "/") return substr(p, 1, 1) == "/"
  return substr(p, 1, length(mp) + 1) == mp "/"
}
' "$inp/df-k.txt")

case "$json" in
  *'"mount":""'*) echo "no filesystem contains $path" >&2; exit 1 ;;
esac

printf '%s\n' "$json" > "$outdir/resources.json"
