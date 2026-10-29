#!/usr/bin/env bash
set -euo pipefail
export LC_NUMERIC=C

config="$IN/config.json"
workload="$IN/workload.py"
raw="$WORK/raw.csv"
sorted="$WORK/sorted.csv"
if command -v python3 >/dev/null; then py=(python3)
elif command -v python >/dev/null; then py=(python)
elif command -v py >/dev/null; then py=(py -3)
else echo "need Python 3" >&2; exit 1
fi

warmups=$(jq -er '.warmups' "$config")
samples=$(jq -er '.samples' "$config")
iterations=$(jq -er '.iterations' "$config")
: > "$raw"
TIMEFORMAT='%3R'

run_case() {
  local name=$1 elapsed output
  if output=$( { time "${py[@]}" "$workload" "$name" "$iterations"; } 2> "$WORK/time.txt"); then
    elapsed=$(cat "$WORK/time.txt")
  else
    echo "benchmark failed: $name" >&2
    return 1
  fi
  [[ "$output" =~ ^[0-9]+$ ]] || { echo "invalid checksum for $name" >&2; return 1; }
  printf '%s\t%s\n' "$elapsed" "$output"
}

while IFS= read -r name; do
  for ((run=1; run<=warmups; run++)); do run_case "$name" > "$WORK/warmup.txt"; done
  checksum=
  for ((run=1; run<=samples; run++)); do
    result=$(run_case "$name")
    elapsed=${result%%$'\t'*}
    output=${result#*$'\t'}
    if [[ -n "$checksum" && "$checksum" != "$output" ]]; then
      echo "checksum changed for $name" >&2; exit 1
    fi
    checksum=$output
    printf '%s,%d,%.6f,%s\n' "$name" "$run" "$elapsed" "$checksum" >> "$raw"
  done
done < <(jq -er '.cases[]' "$config")

LC_ALL=C sort -t, -k1,1 -k2,2n "$raw" > "$sorted"
{
  printf 'case,run,seconds,checksum\n'
  cat "$sorted"
} > "$OUT/samples.csv"
LC_ALL=C sort -t, -k1,1 -k3,3n "$raw" > "$WORK/by-time.csv"
awk -F, '
{
  n[$1]++; value[$1,n[$1]]=$3; sum[$1]+=$3; checksum[$1]=$4
}
END {
  for (name in n) {
    median=value[name,int((n[name]+1)/2)]
    p95=value[name,int(0.95*n[name]+0.999999)]
    printf "%s,%d,%.6f,%.6f,%s\n",name,n[name],median,p95,checksum[name]
  }
}' "$WORK/by-time.csv" | LC_ALL=C sort -t, -k1,1 > "$WORK/summary-rows.csv"
{
  printf 'case,samples,median_seconds,p95_seconds,checksum\n'
  cat "$WORK/summary-rows.csv"
} > "$OUT/summary.csv"
case_count=$(jq -er '.cases | length' "$config")
printf '{"cases":%d,"warmups_per_case":%d,"samples_per_case":%d}\n' \
  "$case_count" "$warmups" "$samples" > "$OUT/summary.json"
