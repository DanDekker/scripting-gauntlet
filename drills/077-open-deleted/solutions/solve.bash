#!/usr/bin/env bash
# 077-open-deleted - field position 10 is the name; the suffix is the marker.
set -euo pipefail
export LC_ALL=C

src="${IN:?IN not set}/lsof.txt"
outdir="${OUT:?OUT not set}"
[[ -r "$src" ]] || { echo "cannot read $src" >&2; exit 1; }
mkdir -p "$outdir"

rows=$(mktemp)
trap 'rm -f "$rows"' EXIT

awk -v rows="$rows" -v outdir="$outdir" '
  NF < 10 || $1 == "COMMAND" { next }
  $5 != "REG" { next }
  $4 !~ /^[0-9]+[rwu]?$/ { next }
  $8 != 0 { next }
  $7 !~ /^[0-9]+$/ { next }
  {
    name = $10; for (i = 11; i <= NF; i++) name = name " " $i
    if (name !~ / \(deleted\)$/) next
    pid = $2
    if (!(pid in first)) { first[pid] = $1; order[++n] = pid }
    bytes[pid] += $7 + 0
    files[pid]++
    total += $7 + 0
    count += 1
  }
  END {
    top = 0
    for (i = 1; i <= n; i++) {
      pid = order[i]
      printf "%s,%s,%.2f,%d\n", pid, first[pid], bytes[pid] / 1048576, files[pid] > rows
      if (top == 0 || bytes[pid] > bytes[top]) top = pid
    }
    printf "{\"processes\":%d,\"files\":%d,\"reclaimable_mb\":%.2f,\"top_pid\":%d}\n", \
      n, count, total / 1048576, top > (outdir "/summary.json")
    close(outdir "/summary.json")
  }' "$src"

{
  printf 'pid,command,bytes_mb,files\n'
  LC_ALL=C sort -t, -k3,3nr -k1,1n "$rows"
} > "$outdir/deleted.csv"
