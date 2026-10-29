#!/usr/bin/env bash
# 029-set-ops — normalize each side to a sorted unique list, then comm.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

a=$(mktemp)
b=$(mktemp)
trap 'rm -f "$a" "$b"' EXIT

normalize() {
  tr -d '\r' < "$1" | awk '
    { gsub(/^[ \t]+|[ \t]+$/, "", $0); if ($0 != "") print tolower($0) }
  ' | LC_ALL=C sort -u
}

normalize "$indir/a.txt" > "$a"
normalize "$indir/b.txt" > "$b"

LC_ALL=C comm -12 "$a" "$b" > "$outdir/both.txt"
LC_ALL=C comm -23 "$a" "$b" > "$outdir/only_a.txt"
LC_ALL=C comm -13 "$a" "$b" > "$outdir/only_b.txt"
LC_ALL=C sort -u "$a" "$b" > "$outdir/union.txt"

na=$(wc -l < "$a" | tr -d ' ')
nb=$(wc -l < "$b" | tr -d ' ')
nb_both=$(wc -l < "$outdir/both.txt" | tr -d ' ')
nb_a=$(wc -l < "$outdir/only_a.txt" | tr -d ' ')
nb_b=$(wc -l < "$outdir/only_b.txt" | tr -d ' ')
nb_u=$(wc -l < "$outdir/union.txt" | tr -d ' ')

summary="$outdir/summary.json"
printf '{"a":%d,"b":%d,"union":%d,"both":%d,"only_a":%d,"only_b":%d}\n' \
  "$na" "$nb" "$nb_u" "$nb_both" "$nb_a" "$nb_b" > "$summary"
