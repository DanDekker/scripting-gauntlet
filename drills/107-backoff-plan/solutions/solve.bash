#!/usr/bin/env bash
# Retry schedule: one awk pass over the log, jq for the config and the summary.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

log="$in_dir/requests.log"
config="$in_dir/config.json"
for f in "$log" "$config"; do
  [ -f "$f" ] || { echo "missing input: $f" >&2; exit 1; }
 done

base=$(jq -r '.base_seconds' "$config")
max_attempts=$(jq -r '.max_attempts' "$config")

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

{
  printf 'request,attempt,wait_seconds\n'
  awk -v base="$base" -v max="$max_attempts" '
    NF >= 4 {
      requests++
      status = $4
      if (status !~ /^[0-9]+$/) { client++; next }
      s = status + 0
      if (s >= 200 && s <= 299) { success++; next }
      if (s == 429 || (s >= 500 && s <= 599)) {
        label = $2 " " $3 " " $4
        for (k = 1; k < max; k++) {
          wait = base * (2 ^ (k - 1))
          printf "%s,%d,%d\n", label, k, wait
          retries++
          total += wait
        }
        if (1 + (max - 1) >= max) exhausted++
        retryable++
        next
      }
      client++
    }
    END { printf "%d %d %d %d %d %d %d\n", requests + 0, success + 0, retryable + 0, client + 0, retries + 0, exhausted + 0, total + 0 > counts_out }
  ' counts_out="$scratch/counts.txt" "$log"
} > "$out_dir/schedule.csv"

read -r n_requests n_success n_retryable n_client n_retries n_exhausted n_total < "$scratch/counts.txt"

jq -n \
  --argjson requests "$n_requests" \
  --argjson success "$n_success" \
  --argjson retryable "$n_retryable" \
  --argjson client_errors "$n_client" \
  --argjson retries "$n_retries" \
  --argjson exhausted "$n_exhausted" \
  --argjson total_wait "$n_total" \
  '{requests: $requests, success: $success, retryable: $retryable, client_errors: $client_errors, retries: $retries, exhausted: $exhausted, total_wait: $total_wait}' \
  > "$out_dir/summary.json"
