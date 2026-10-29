#!/usr/bin/env bash
# Diff two prompt versions with awk: normalize, dedupe, set-difference, classify.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# Normalize: strip CR, collapse whitespace runs, trim, drop empties, drop duplicates
# (first occurrence wins, order preserved).
normalize() {
  awk '
    {
      sub(/\r$/, "")
      gsub(/[[:space:]]+/, " ")
      sub(/^ /, "")
      sub(/ $/, "")
      if ($0 == "") next
      if (seen[$0]++) next
      print
    }
  ' "$1"
}

normalize "$in_dir/prompt_v1.txt" > "$scratch/v1.txt"
normalize "$in_dir/prompt_v2.txt" > "$scratch/v2.txt"

# FILENAME-based tagging survives an empty left-hand file, unlike NR == FNR.
awk 'FILENAME == ARGV[1] { in_v2[$0] = 1; next } !($0 in in_v2)' \
  "$scratch/v2.txt" "$scratch/v1.txt" > "$scratch/removed.txt"
awk 'FILENAME == ARGV[1] { in_v1[$0] = 1; next } !($0 in in_v1)' \
  "$scratch/v1.txt" "$scratch/v2.txt" > "$scratch/added.txt"

unchanged=$(awk 'FILENAME == ARGV[1] { in_v2[$0] = 1; next } ($0 in in_v2)' \
  "$scratch/v2.txt" "$scratch/v1.txt" | wc -l | tr -d ' ')
removed_n=$(wc -l < "$scratch/removed.txt" | tr -d ' ')
added_n=$(wc -l < "$scratch/added.txt" | tr -d ' ')

guardrails=$(awk -v pat="must|never|do not|don't|should not" \
  'tolower($0) ~ pat { c++ } END { print c + 0 }' "$scratch/removed.txt")

# Minimal CSV quoting, matching csv.writer defaults.
{
  printf 'change,line\n'
  awk -v r="$scratch/removed.txt" '
    function q(s) {
      if (index(s, ",") || index(s, "\"")) {
        gsub(/"/, "\"\"", s)
        return "\"" s "\""
      }
      return s
    }
    { printf "%s,%s\n", (FILENAME == r ? "removed" : "added"), q($0) }
  ' "$scratch/removed.txt" "$scratch/added.txt"
} > "$out_dir/changes.csv"

jq -n \
  --argjson removed "$removed_n" \
  --argjson added "$added_n" \
  --argjson unchanged "$unchanged" \
  --argjson guardrails "$guardrails" \
  '{removed: $removed, added: $added, unchanged: $unchanged,
    guardrails_removed: $guardrails}' > "$out_dir/summary.json"
