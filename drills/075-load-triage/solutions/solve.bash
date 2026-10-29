#!/usr/bin/env bash
# 075-load-triage - one awk pass per host, verdict from the averages.
set -euo pipefail

hosts_dir="${IN:?IN not set}/hosts"
outdir="${OUT:?OUT not set}"
[[ -d "$hosts_dir" ]] || { echo "missing $hosts_dir" >&2; exit 1; }
mkdir -p "$outdir"

rows=$(mktemp)
trap 'rm -f "$rows"' EXIT

for dir in "$hosts_dir"/*/; do
  host=$(basename "$dir")
  for f in nproc loadavg vmstat; do
    [[ -r "$dir$f" ]] || { echo "$host: cannot read $f" >&2; exit 1; }
  done
  nproc=$(tr -d '[:space:]' < "$dir/nproc")
  [[ "$nproc" =~ ^[1-9][0-9]*$ ]] || { echo "$host: bad nproc" >&2; exit 1; }
  load1=$(awk 'NR == 1 { print $1 }' "$dir/loadavg")
  [[ "$load1" =~ ^[0-9]+(\.[0-9]+)?$ ]] || { echo "$host: bad loadavg" >&2; exit 1; }
  awk -v host="$host" -v nproc="$nproc" -v load1="$load1" '
    $1 ~ /^[0-9]+$/ && NF >= 17 {
      n++
      r = $1 + 0; si = $7 + 0; so = $8 + 0
      us = $13 + 0; sy = $14 + 0; wa = $16 + 0
      sum_r += r; sum_wa += wa; sum_busy += us + sy
      if (si + so > 0) swapped = 1
    }
    END {
      if (n == 0) { print host ": no vmstat samples" > "/dev/stderr"; exit 1 }
      r_avg = sum_r / n; wa_avg = sum_wa / n; busy = sum_busy / n
      if (swapped) verdict = "memory"
      else if (wa_avg >= 10) verdict = "io"
      else if (r_avg >= 2 * nproc && busy >= 80) verdict = "cpu"
      else verdict = "healthy"
      printf "%s,%s,%.2f,%.1f,%.1f,%.1f\n", host, verdict, load1 / nproc, r_avg, wa_avg, busy
    }' "$dir/vmstat" >> "$rows"
done

{
  printf 'host,verdict,load1_per_cpu,r_avg,wa_avg,busy_pct\n'
  LC_ALL=C sort -t, -k1,1 "$rows"
} > "$outdir/triage.csv"

hosts=$(awk 'END { print NR }' "$rows")
saturated=$(awk -F, '$2 != "healthy"' "$rows" | awk 'END { print NR }')
printf '{"hosts":%d,"saturated":%d}\n' "$hosts" "$saturated" > "$outdir/summary.json"
