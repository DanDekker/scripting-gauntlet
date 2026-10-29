#!/usr/bin/env bash
# Pick the tests to run by walking the import graph breadth-first in awk.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

for f in "$in_dir/graph.csv" "$in_dir/changes.txt"; do
  [ -f "$f" ] || { echo "missing $f" >&2; exit 1; }
 done

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

# Every module named in the module column is a key, even with a blank import.
awk -F',' '
  { sub(/\r$/, "") }
  NR == 1 {
    m = $1; gsub(/^[ \t]+|[ \t]+$/, "", m)
    if (m == "module") next
  }
  {
    m = $1; gsub(/^[ \t]+|[ \t]+$/, "", m)
    if (m == "") next
    print m
  }
' "$in_dir/graph.csv" | sort -u > "$scratch/keys.txt"

# Deduped edges: no blank imports, no self-imports.
awk -F',' '
  { sub(/\r$/, "") }
  NR == 1 {
    m = $1; i2 = $2
    gsub(/^[ \t]+|[ \t]+$/, "", m); gsub(/^[ \t]+|[ \t]+$/, "", i2)
    if (m == "module" && i2 == "imports") next
  }
  {
    m = $1; i2 = $2
    gsub(/^[ \t]+|[ \t]+$/, "", m); gsub(/^[ \t]+|[ \t]+$/, "", i2)
    if (m == "" || i2 == "" || m == i2) next
    print m "\t" i2
  }
' "$in_dir/graph.csv" | sort -u > "$scratch/edges.tsv"

# Changes: trim, drop blanks, dedupe, then name the module each path points at.
awk '
  {
    line = $0
    sub(/\r$/, "", line)
    gsub(/^[ \t]+|[ \t]+$/, "", line)
    if (line != "") print line
  }
' "$in_dir/changes.txt" | sort -u | awk '
  {
    n = split($0, parts, "/")
    base = parts[n]
    dot = 0
    for (i = length(base); i > 0; i--) if (substr(base, i, 1) == ".") { dot = i; break }
    if (dot > 1) base = substr(base, 1, dot - 1)
    print $0 "\t" base
  }
' > "$scratch/changed.tsv"

# Known vs unknown: classify each distinct changed path once.
awk -F'\t' '
  FILENAME == ARGV[1] { key[$0] = 1; next }
  ($2 in key) { print $2 }
' "$scratch/keys.txt" "$scratch/changed.tsv" | sort -u > "$scratch/known_modules.txt"

awk -F'\t' '
  FILENAME == ARGV[1] { key[$0] = 1; next }
  ($2 in key) { known++; next }
  { unknown++ }
  END { print known + 0, unknown + 0 }
' "$scratch/keys.txt" "$scratch/changed.tsv" > "$scratch/counts.txt"
read -r n_known n_unknown < "$scratch/counts.txt"

# Test files are the graph modules under tests/, with the module they exercise.
awk '
  index($0, "tests/") == 1 && length($0) > 6 {
    n = split($0, parts, "/")
    base = parts[n]
    dot = 0
    for (i = length(base); i > 0; i--) if (substr(base, i, 1) == ".") { dot = i; break }
    if (dot > 1) base = substr(base, 1, dot - 1)
    print $0 "\t" base
  }
' "$scratch/keys.txt" | sort > "$scratch/tests.tsv"

# Only roots that are keys can reach anything.
cut -f2 "$scratch/tests.tsv" | sort -u > "$scratch/stems.txt"
awk '
  FILENAME == ARGV[1] { key[$0] = 1; next }
  ($0 in key)
' "$scratch/keys.txt" "$scratch/stems.txt" > "$scratch/roots.txt"

# Breadth-first closure per root. Emits <reachable module> TAB <root>.
awk -F'\t' '
  FILENAME == ARGV[1] { adj[$1] = adj[$1] "\t" $2; next }
  {
    start = $0
    delete seen
    split("", queue)
    seen[start] = 1
    head = 1; tail = 1; queue[1] = start
    while (head <= tail) {
      cur = queue[head]; head++
      count = split(adj[cur], nexts, "\t")
      for (j = 1; j <= count; j++) {
        v = nexts[j]
        if (v != "" && !(v in seen)) { seen[v] = 1; queue[++tail] = v }
      }
    }
    for (k in seen) print k "\t" start
  }
' "$scratch/edges.tsv" "$scratch/roots.txt" | sort -u > "$scratch/reach.tsv"

# A root is hit when a known changed module sits in its closure.
awk -F'\t' '
  FILENAME == ARGV[1] { changed[$0] = 1; next }
  ($1 in changed) { print $2 }
' "$scratch/known_modules.txt" "$scratch/reach.tsv" | sort -u > "$scratch/hit_roots.txt"

awk -F'\t' '
  FILENAME == ARGV[1] { hit[$0] = 1; next }
  ($2 in hit) { print $1 }
' "$scratch/hit_roots.txt" "$scratch/tests.tsv" | sort > "$scratch/selected.txt"

cp "$scratch/selected.txt" "$out_dir/selected.txt"

n_changes=$(wc -l < "$scratch/changed.tsv" | tr -d ' ')
n_tests=$(wc -l < "$scratch/tests.tsv" | tr -d ' ')
n_selected=$(wc -l < "$scratch/selected.txt" | tr -d ' ')

jq -n \
  --argjson changes "$n_changes" \
  --argjson known "$n_known" \
  --argjson unknown "$n_unknown" \
  --argjson tests "$n_tests" \
  --argjson selected "$n_selected" \
  --argjson unused "$((n_tests - n_selected))" \
  '{changes: $changes, known: $known, unknown: $unknown, tests: $tests, selected: $selected, unused: $unused}' \
  > "$out_dir/summary.json"
