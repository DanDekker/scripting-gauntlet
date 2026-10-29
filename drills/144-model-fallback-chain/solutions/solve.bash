#!/usr/bin/env bash
# Replay the attempt log through the tier chain with awk.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -R -r 'fromjson? | select(type == "object" and has("task_id")) | .task_id | tostring' \
  "$in_dir/tasks.jsonl" | sort -u > "$scratch/tasks.txt"

jq -r '.[] | [(.tier | tostring), (.timeout_ms | tostring), ((.max_retries // 0) | tostring)] | @tsv' \
  "$in_dir/providers.json" | sort -t $'\t' -k1,1n > "$scratch/tiers.txt"

awk -F, '
  NR == 1 { next }
  {
    line = $0
    sub(/^[ \t\r]+/, "", line)
    sub(/[ \t\r]+$/, "", line)
    if (line == "") next
    if (split(line, f, ",") != 5) next
    for (i = 1; i <= 5; i++) { sub(/^[ \t]+/, "", f[i]); sub(/[ \t]+$/, "", f[i]) }
    if (f[1] == "" || f[2] !~ /^[0-9]+$/ || f[3] !~ /^[0-9]+$/ || f[4] !~ /^[0-9]+$/ || f[5] !~ /^[0-9]+$/) next
    printf "%s\t%s\t%s\t%s\t%s\n", f[1], f[2], f[3], f[4], f[5]
  }' "$in_dir/attempts.csv" > "$scratch/attempts.tsv"

awk -F'\t' -v sumfile="$scratch/summary.tsv" '
  FILENAME ~ /tasks/ { nt++; tasks[nt] = $1; next }
  FILENAME ~ /tiers/ { nT++; tier[nT] = $1; tmo[$1] = $2 + 0; mret[$1] = $3 + 0; next }
  {
    key = $1 SUBSEP $2 SUBSEP $3
    astatus[key] = $4 + 0
    alat[key] = $5 + 0
    present[key] = 1
  }
  END {
    success = 0; failed = 0; fallback = 0; grand = 0
    for (i = 1; i <= nt; i++) {
      task = tasks[i]
      outcome = "failed"; resolved = ""; count = 0; sum = 0; done = 0
      for (j = 1; j <= nT && !done; j++) {
        t = tier[j]
        cap = mret[t] + 1
        for (a = 1; a <= cap; a++) {
          key = task SUBSEP t SUBSEP a
          if (!(key in present)) break
          count++
          sum += alat[key]
          if (astatus[key] == 200 && alat[key] <= tmo[t]) {
            outcome = "success"; resolved = t; done = 1; break
          }
        }
      }
      if (outcome == "success") {
        success++
        if (resolved + 0 > 1) fallback++
      } else {
        failed++
      }
      grand += sum
      printf "%s,%s,%s,%d,%d\n", task, outcome, resolved, count, sum
    }
    printf "%d\t%d\t%d\t%d\t%d\n", nt, success, failed, fallback, grand > sumfile
  }
' "$scratch/tasks.txt" "$scratch/tiers.txt" "$scratch/attempts.tsv" > "$scratch/resolutions.csv"

{
  printf 'task_id,outcome,resolved_tier,attempts_count,total_latency_ms\n'
  cat "$scratch/resolutions.csv"
} > "$out_dir/resolutions.csv"

IFS=$'\t' read -r total success failed fallback grand < "$scratch/summary.tsv"

jq -n \
  --argjson total_tasks "$total" \
  --argjson success_count "$success" \
  --argjson failed_count "$failed" \
  --argjson fallback_invoked "$fallback" \
  --argjson total_latency_ms "$grand" \
  '{total_tasks: $total_tasks, success_count: $success_count, failed_count: $failed_count,
    fallback_invoked: $fallback_invoked, total_latency_ms: $total_latency_ms}' > "$out_dir/summary.json"
