#!/usr/bin/env bash
# 053-fd-limits — count rows per pid, then compare against the soft limit.
set -euo pipefail

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
for f in fd-listing.txt fd-limit.txt; do
  [ -r "$inp/$f" ] || { echo "cannot read $inp/$f" >&2; exit 1; }
done
mkdir -p "$outdir"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

limit=$(awk '
/^[[:space:]]*#/ { next }
NF == 0 { next }
{
  for (i = 1; i <= NF; i++) if ($i ~ /^[0-9]+$/) { print $i + 0; exit }
}
' "$inp/fd-limit.txt")
[ -n "$limit" ] || { echo "no integer limit in fd-limit.txt" >&2; exit 1; }

awk -v counts="$tmp/counts.body" -v total="$tmp/descriptors" '
$1 ~ /^[0-9]+$/ {
  c[$1 + 0]++
  d++
}
END {
  for (p in c) printf "%d,%d\n", p, c[p] > counts
  printf "%d\n", d > total
  close(counts)
  close(total)
}
' "$inp/fd-listing.txt"

{
  printf 'pid,descriptors\n'
  LC_ALL=C sort -t, -k2,2nr -k1,1n "$tmp/counts.body"
} > "$outdir/fd-counts.csv"

{
  printf 'pid,descriptors,limit\n'
  awk -F, -v lim="$limit" '$2 + 0 >= lim { printf "%d,%d,%d\n", $1 + 0, $2 + 0, lim }' \
    "$tmp/counts.body" | LC_ALL=C sort -t, -k1,1n
} > "$outdir/flagged.csv"

processes=$(awk 'END { print NR + 0 }' "$tmp/counts.body")
descriptors=$(cat "$tmp/descriptors")
flagged=$(awk 'END { print NR + 0 }' "$outdir/flagged.csv")
flagged=$((flagged > 0 ? flagged - 1 : 0))
printf '{"processes":%d,"descriptors":%d,"limit":%d,"flagged":%d}\n' \
  "$processes" "$descriptors" "$limit" "$flagged" > "$outdir/summary.json"
