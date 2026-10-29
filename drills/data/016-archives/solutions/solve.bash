#!/usr/bin/env bash
# 016-archives — decompress to stdout, list members before extracting one.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

sources=0
for path in "$indir"/*.tar.gz; do
  [ -e "$path" ] || continue
  sources=$((sources + 1))
  tar -tzf "$path" | grep '\.csv$' | while IFS= read -r member; do
    tar -xzOf "$path" "$member"
  done >> "$body"
done

for path in "$indir"/*.csv.gz; do
  [ -e "$path" ] || continue
  sources=$((sources + 1))
  gzip -dc "$path" >> "$body"
done

awk -F',' -v files="$sources" -v summary="$outdir/summary.json" '
$1 == "id" { next }          # every source carries its own header
{
  region = $2; amount = $3 + 0
  total[region] += amount
  count[region]++
  rows++
}
END {
  n = 0
  for (region in total) keys[++n] = region
  for (i = 2; i <= n; i++) {
    v = keys[i]; j = i - 1
    while (j >= 1 && (total[keys[j]] < total[v] || (total[keys[j]] == total[v] && keys[j] > v))) {
      keys[j + 1] = keys[j]; j--
    }
    keys[j + 1] = v
  }
  print "region,amount,rows"
  for (i = 1; i <= n; i++) printf "%s,%.2f,%d\n", keys[i], total[keys[i]], count[keys[i]]
  printf "{\"files\":%d,\"rows\":%d}\n", files, rows > summary
  close(summary)
}' "$body" > "$outdir/by_region.csv"
