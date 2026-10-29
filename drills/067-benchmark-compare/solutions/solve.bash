#!/usr/bin/env bash
set -euo pipefail
export LC_NUMERIC=C

raw="$WORK/combined.csv"
sorted="$WORK/sorted.csv"
: > "$raw"
for side in baseline candidate; do
  file="$IN/$side.csv"
  [[ -r "$file" ]] || { echo "cannot read: $file" >&2; exit 1; }
  awk -F, -v side="$side" 'FNR > 1 { print side "," $1 "," $2 "," $4 }' "$file" >> "$raw"
done
LC_ALL=C sort -t, -k2,2 -k3,3 -k1,1 -k4,4n "$raw" > "$sorted"

{
  printf 'platform,case,baseline_median_ms,candidate_median_ms,change_pct,status\n'
  awk -F, -v summary="$OUT/summary.json" '
function finish() {
  if (key == "") return
  if (nb != 3 || nc != 3 || b[2] <= 0) {
    print "expected three positive samples for " platform "/" case_name > "/dev/stderr"
    bad = 1
    return
  }
  change = ((c[2] - b[2]) / b[2]) * 100
  rounded = sprintf("%.1f", change) + 0
  status = rounded > 10.0 ? "regression" : "ok"
  printf "%s,%s,%.1f,%.1f,%.1f,%s\n", platform, case_name, b[2], c[2], rounded, status
  comparisons++
  if (status == "regression") regressions++
}
{
  next_key = $2 SUBSEP $3
  if (key != "" && key != next_key) { finish(); nb=0; nc=0 }
  if (key != next_key) { key=next_key; platform=$2; case_name=$3 }
  if ($4 <= 0) { print "non-positive timing for " $2 "/" $3 > "/dev/stderr"; bad=1; next }
  if ($1 == "baseline") b[++nb] = $4
  else if ($1 == "candidate") c[++nc] = $4
  else { print "unknown sample set: " $1 > "/dev/stderr"; bad=1 }
}
END {
  finish()
  printf "{\"comparisons\":%d,\"regressions\":%d,\"threshold_pct\":10}\n", comparisons, regressions > summary
  if (bad || comparisons == 0) exit 1
}' "$sorted"
} > "$OUT/comparison.csv"
