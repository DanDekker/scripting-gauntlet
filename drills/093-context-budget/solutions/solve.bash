#!/usr/bin/env bash
# Greedy context packer with awk + sort: dedupe last-wins, priority/path order, fill.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

budget=$(tr -d '[:space:]' < "$in_dir/budget.txt")

# One candidate per path (last valid row wins), emitted as path<TAB>tokens<TAB>priority.
awk -F',' '
  function trim(s) {
    gsub(/^[[:space:]]+/, "", s)
    gsub(/[[:space:]]+$/, "", s)
    return s
  }
  {
    p = trim($1); t = trim($2); pr = trim($3)
    if (p == "") next
    if (tolower(p) == "path" && tolower(t) == "tokens") next
    if (t !~ /^[0-9]+$/) next
    if (pr !~ /^-?[0-9]+$/) next
    tokens[p] = t + 0
    priority[p] = pr + 0
    seen[p] = 1
  }
  END { for (p in seen) print p "\t" tokens[p] "\t" priority[p] }
' "$in_dir/files.csv" > "$scratch/candidates.tsv"

# Deterministic order: priority ascending, then path byte order.
LC_ALL=C sort -t "$(printf '\t')" -k3,3n -k1,1 "$scratch/candidates.tsv" > "$scratch/order.tsv"

awk -F'\t' -v budget="$budget" -v stats="$scratch/stats" '
  BEGIN { remaining = budget }
  {
    if ($2 <= remaining) {
      print $1
      remaining -= $2
      included++
    } else {
      skipped++
    }
  }
  END {
    printf "%d %d %d %d %d\n", budget, included, budget - remaining, skipped, remaining > stats
  }
' "$scratch/order.tsv" > "$out_dir/context.txt"

read -r s_budget s_included s_tokens s_skipped s_remaining < "$scratch/stats"

jq -n \
  --argjson budget "$s_budget" \
  --argjson included "$s_included" \
  --argjson tokens "$s_tokens" \
  --argjson skipped "$s_skipped" \
  --argjson remaining "$s_remaining" \
  '{budget: $budget, included: $included, included_tokens: $tokens,
    skipped: $skipped, remaining: $remaining}' > "$out_dir/summary.json"
