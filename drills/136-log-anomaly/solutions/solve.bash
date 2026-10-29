#!/usr/bin/env bash
# Flag error-rate spikes with a single awk pass over the minute table: a ring of the last
# `window` minutes keeps the baseline a ratio of sums, not a mean of rates.
set -euo pipefail

export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

window=$(jq -r '.window' "$in_dir/thresholds.json")
minreq=$(jq -r '.min_requests' "$in_dir/thresholds.json")
mult=$(jq -r '.rate_multiplier' "$in_dir/thresholds.json")
minrate=$(jq -r '.min_rate' "$in_dir/thresholds.json")

awk -v window="$window" -v minreq="$minreq" -v mult="$mult" -v minrate="$minrate" \
    -v rowsfile="$out_dir/anomalies.csv" -v sumfile="$scratch/summary.tsv" -F, '
  function trim(s) { gsub(/^[ \t\r]+/, "", s); gsub(/[ \t\r]+$/, "", s); return s }

  BEGIN {
    total = 0; evaluated = 0; found = 0; count = 0
    print "minute,requests,errors,error_rate,baseline_rate,culprit" > rowsfile
    for (k in window_errors) delete window_errors[k]
  }

  {
    minute = trim($1)
    req = trim($2)
    err = trim($3)
    top = (NF >= 4 ? trim($4) : "")
    if (minute == "" || minute == "minute") next
    if (req !~ /^[0-9]+$/ || err !~ /^[0-9]+$/) next
    requests = req + 0
    errors = err + 0
    rate = (requests == 0 ? 0.0 : errors / requests)

    if (count >= window && requests >= minreq) {
      evaluated++
      wr = 0; we = 0
      for (i = count - window; i < count; i++) { we += hist_err[i]; wr += hist_req[i] }
      baseline = (wr == 0 ? 0.0 : we / wr)
      if (rate >= minrate && rate >= baseline * mult) {
        culprit = (top == "" ? "Unknown" : top)
        printf "%s,%d,%d,%.4f,%.4f,%s\n", minute, requests, errors, rate, baseline, culprit >> rowsfile
        found++
        tally[culprit]++
      }
    }

    hist_err[count] = errors
    hist_req[count] = requests
    count++
    total++
  }

  END {
    best = -1; best_name = ""
    for (name in tally) {
      if (tally[name] > best || (tally[name] == best && name < best_name)) {
        best = tally[name]; best_name = name
      }
    }
    print "total_minutes\t" total > sumfile
    print "evaluated_minutes\t" evaluated > sumfile
    print "anomaly_minutes\t" found > sumfile
    print "top_culprit\t" (best > 0 ? best_name : "") > sumfile
  }
' "$in_dir/traffic.csv"

total=$(awk -F'\t' '$1 == "total_minutes" { print $2 }' "$scratch/summary.tsv")
evaluated=$(awk -F'\t' '$1 == "evaluated_minutes" { print $2 }' "$scratch/summary.tsv")
found=$(awk -F'\t' '$1 == "anomaly_minutes" { print $2 }' "$scratch/summary.tsv")
top=$(awk -F'\t' '$1 == "top_culprit" { print $2 }' "$scratch/summary.tsv")

jq -n \
  --argjson total "$total" \
  --argjson evaluated "$evaluated" \
  --argjson found "$found" \
  --arg top "$top" \
  '{total_minutes: $total, evaluated_minutes: $evaluated,
    anomaly_minutes: $found, top_culprit: $top}' > "$out_dir/summary.json"
