#!/usr/bin/env bash
# 078-cleanup-budget - three-key sort, then stop on the threshold.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
[[ -r "$inp/candidates.csv" && -r "$inp/target.txt" ]] \
  || { echo "missing candidates.csv or target.txt" >&2; exit 1; }
mkdir -p "$outdir"

target=$(tr -d '[:space:]' < "$inp/target.txt")
[[ "$target" =~ ^[0-9]+$ ]] || { echo "bad target: $target" >&2; exit 1; }

picked=$(mktemp)
trap 'rm -f "$picked"' EXIT

awk -F, '
  $1 ~ /^[[:space:]]*$/ || $1 ~ /^[[:space:]]*#/ { next }
  $2 !~ /^[0-9]+$/ || $3 !~ /^[0-9]+$/ { next }
  { printf "%d,%d,%s,%d\n", $3 + 0, $2 + 0, $1, $2 + 0 }
' "$inp/candidates.csv" \
  | LC_ALL=C sort -t, -k1,1n -k2,2nr -k3,3 \
  | awk -F, -v target="$target" -v picked="$picked" -v outdir="$outdir" '
  BEGIN { freed = 0; taken = 0 }
  {
    if (freed >= target) next
    freed += $2; taken += 1
    printf "%d,%s,%d,%d\n", taken, $3, $2, $1 > picked
  }
  END {
    complete = (freed >= target) ? "true" : "false"
    printf "{\"target_mb\":%d,\"freed_mb\":%d,\"taken\":%d,\"complete\":%s}\n", \
      target, freed, taken, complete > (outdir "/summary.json")
    close(outdir "/summary.json")
  }'

{
  printf 'order,path,size_mb,risk\n'
  cat "$picked"
} > "$outdir/cleanup.csv"
