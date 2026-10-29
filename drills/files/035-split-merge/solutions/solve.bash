#!/usr/bin/env bash
# 035-split-merge — split into fixed-size chunks, then prove the roundtrip.
set -euo pipefail

src="${IN:?IN not set}/events.csv"
outdir="${OUT:?OUT not set}"
CHUNK=5
[ -f "$src" ] || { echo "no such file: $src" >&2; exit 1; }
mkdir -p "$outdir"

read -r rows chunks <<< "$(LC_ALL=C awk -v n="$CHUNK" -v dir="$outdir" '
NR == 1 { header = $0; next }
{
  bucket = int((NR - 2) / n) + 1
  target = sprintf("%s/chunk_%02d.csv", dir, bucket)
  if (!(bucket in opened)) { print header > target; opened[bucket] = 1 }
  print > target
  data++
}
END {
  total = int((data + n - 1) / n)
  for (i = 1; i <= total; i++) close(sprintf("%s/chunk_%02d.csv", dir, i))
  printf "%d %d\n", data, total
}' "$src")"

[ "$rows" -gt 0 ] || { echo "no data rows in $src" >&2; exit 1; }

: > "$outdir/merged.csv"
first=1
for chunk in "$outdir"/chunk_*.csv; do
  if [ "$first" -eq 1 ]; then
    cat "$chunk" >> "$outdir/merged.csv"
    first=0
  else
    tail -n +2 "$chunk" >> "$outdir/merged.csv"
  fi
done

cmp -s "$outdir/merged.csv" "$src" \
  || { echo "reassembly does not match $src" >&2; exit 1; }

printf '{"rows":%d,"chunk_size":%d,"chunks":%d,"roundtrip":true}\n' \
  "$rows" "$CHUNK" "$chunks" > "$outdir/report.json"
