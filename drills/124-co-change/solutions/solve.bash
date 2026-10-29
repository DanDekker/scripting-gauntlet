#!/usr/bin/env bash
# 124-co-change - awk folds the log into commit blocks and counts pairs; sort orders them.
set -euo pipefail
export LC_ALL=C

log="${IN:?IN not set}/log.txt"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"
[[ -f "$log" ]] || { echo "missing $log" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk -v rows="$scratch/rows.csv" -v counts="$scratch/counts.tsv" '
function trim(s) { sub(/^[ \t\r]+/, "", s); sub(/[ \t\r]+$/, "", s); return s }
{
  t = trim($0)
  if (t == "commit" || t ~ /^commit /) { blk++; nf[blk] = 0; next }
  if (blk == 0) next
  if (t == "") next
  if ((blk SUBSEP t) in seen) next
  seen[blk SUBSEP t] = 1
  f[blk, ++nf[blk]] = t
}
END {
  for (b = 1; b <= blk; b++) {
    if (nf[b] == 0) continue
    commits++
    for (i = 1; i <= nf[b]; i++) touched[f[b, i]]++
    for (i = 1; i <= nf[b]; i++) {
      for (j = i + 1; j <= nf[b]; j++) {
        a = f[b, i]; c = f[b, j]
        if (a > c) { swap = a; a = c; c = swap }
        shared[a SUBSEP c]++
      }
    }
  }
  pairs = 0
  for (k in shared) {
    if (shared[k] < 2) continue
    split(k, p, SUBSEP)
    union = touched[p[1]] + touched[p[2]] - shared[k]
    printf "%s,%s,%d,%.4f\n", p[1], p[2], shared[k], shared[k] / union >> rows
    pairs++
  }
  files = 0
  for (n in touched) files++
  printf "%d\t%d\t%d\n", commits, files, pairs > counts
}' "$log"

{
  printf 'file_a,file_b,shared,score\n'
  sort -t',' -k3,3nr -k4,4nr -k1,1 -k2,2 "$scratch/rows.csv"
} > "$outdir/pairs.csv"

read -r commits files pairs < "$scratch/counts.tsv"
most=$(sed -n '2p' "$outdir/pairs.csv" | cut -d',' -f1)
printf '{"commits":%d,"coupled_pairs":%d,"files":%d,"most_coupled":"%s"}\n' \
  "$commits" "$pairs" "$files" "$most" > "$outdir/summary.json"
