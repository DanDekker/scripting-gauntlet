#!/usr/bin/env bash
# Triage a CI log with awk: strip ANSI, keep result lines, last verdict wins except ERROR.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

if [ ! -f "$in_dir/ci.log" ]; then
  echo "no such file: $in_dir/ci.log" >&2
  exit 1
fi

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk '
  {
    line = $0
    gsub(/\033\[[0-9;]*m/, "", line)
    sub(/^[ \t]+/, "", line)
    sub(/[ \t\r]+$/, "", line)
    if (line == "=== short test summary info ===") { summary = 1; next }
    n = split(line, token, /[ \t]+/)
    if (n < 2) next
    status = token[1]
    if (status != "PASSED" && status != "FAILED" && status != "ERROR" && status != "SKIP") next
    if (summary && status != "FAILED") next
    test = token[2]
    if (!(test in seen)) { seen[test] = 1; order[++count] = test }
    last[test] = status
    if (status == "ERROR") sticky[test] = 1
  }
  END {
    for (i = 1; i <= count; i++) {
      test = order[i]
      status = last[test]
      if (sticky[test]) status = "ERROR"
      verdict = (status == "PASSED" ? "pass" \
                 : status == "FAILED" ? "fail" \
                 : status == "ERROR" ? "error" : "skip")
      printf "%s\t%s\n", test, verdict
    }
  }
' "$in_dir/ci.log" | LC_ALL=C sort -t$'\t' -k1,1 > "$scratch/rows.tsv"

{
  printf 'test,verdict\n'
  awk -F'\t' 'function q(s) {
      if (index(s, ",") || index(s, "\"")) {
        gsub(/"/, "\"\"", s)
        return "\"" s "\""
      }
      return s
    }
    { printf "%s,%s\n", q($1), q($2) }' "$scratch/rows.tsv"
} > "$out_dir/results.csv"

tests=$(awk 'END { print NR }' "$scratch/rows.tsv")
passed=$(awk -F'\t' '$2 == "pass" { n++ } END { print n + 0 }' "$scratch/rows.tsv")
failed=$(awk -F'\t' '$2 == "fail" { n++ } END { print n + 0 }' "$scratch/rows.tsv")
errored=$(awk -F'\t' '$2 == "error" { n++ } END { print n + 0 }' "$scratch/rows.tsv")
skipped=$(awk -F'\t' '$2 == "skip" { n++ } END { print n + 0 }' "$scratch/rows.tsv")

jq -n \
  --argjson tests "$tests" \
  --argjson passed "$passed" \
  --argjson failed "$failed" \
  --argjson errored "$errored" \
  --argjson skipped "$skipped" \
  '{tests: $tests, passed: $passed, failed: $failed, errored: $errored, skipped: $skipped}' \
  > "$out_dir/summary.json"
