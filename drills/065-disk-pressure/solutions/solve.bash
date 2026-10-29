#!/usr/bin/env bash
set -euo pipefail

linux="$IN/linux/df.txt"
macos="$IN/macos/df.txt"
windows="$IN/windows/volumes.csv"
all="$WORK/volumes.csv"
low="$WORK/low.csv"
for path in "$linux" "$macos" "$windows"; do
  [[ -r "$path" ]] || { echo "cannot read: $path" >&2; exit 1; }
done
: > "$all"

awk -v platform=linux '
NR > 1 && NF >= 6 {
  if ($2 <= 0) { print "zero-sized Linux volume: " $6 > "/dev/stderr"; exit 1 }
  mount=$6; for (i=7; i<=NF; i++) mount=mount " " $i
  printf "%s,%s,%.0f,%.0f,%.1f\n", platform, mount, $2*1024, $4*1024, 100*$4/$2
}' "$linux" >> "$all"
awk -v platform=macos '
NR > 1 && NF >= 9 {
  if ($2 <= 0) { print "zero-sized macOS volume: " $9 > "/dev/stderr"; exit 1 }
  mount=$9; for (i=10; i<=NF; i++) mount=mount " " $i
  printf "%s,%s,%.0f,%.0f,%.1f\n", platform, mount, $2*1024, $4*1024, 100*$4/$2
}' "$macos" >> "$all"
awk -F, '
NR > 1 {
  total=$3+0; free=$4+0
  if (total <= 0) { print "zero-sized Windows volume: " $1 > "/dev/stderr"; exit 1 }
  volume=$1 ":\\ (" $2 ")"
  printf "windows,%s,%.0f,%.0f,%.1f\n", volume, total, free, 100*free/total
}' "$windows" >> "$all"

awk -F, -v summary="$OUT/summary.json" '
BEGIN { print "platform,volume,total_bytes,free_bytes,free_pct" }
{
  seen++
  if ($5+0 <= 10) { print; low++ }
}
END { printf "{\"volumes_seen\":%d,\"low_space\":%d}\n", seen, low > summary }
' "$all" | { IFS= read -r header; printf '%s\n' "$header"; LC_ALL=C sort -t, -k5,5n -k1,1 -k2,2; } > "$low"
cp "$low" "$OUT/low_space.csv"
