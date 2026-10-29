#!/usr/bin/env bash
# Changelog with a single awk pass: parse, group, print the sections in order.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

source_file="$in_dir/commits.txt"
[ -f "$source_file" ] || { echo "missing input: $source_file" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk '
  function trim(s) { gsub(/^[ \t\r]+/, "", s); gsub(/[ \t\r]+$/, "", s); return s }
  BEGIN { n = 0; commits = 0; conv = 0; skipped = 0; prev = 0 }
  {
    line = $0
    sub(/\r$/, "", line)
    line = trim(line)
    if (line == "") next
    if (line ~ /^BREAKING CHANGE:/) {
      if (prev > 0) brk[prev] = 1
      next
    }
    commits++
    if (!match(line, /^(feat|fix|docs|refactor|perf|test|chore|build|ci)(\([^)]*\))?(!)?: /)) {
      skipped++
      prev = 0
      next
    }
    head = substr(line, 1, RLENGTH)
    rest = substr(line, RLENGTH + 1)
    match(head, /^(feat|fix|docs|refactor|perf|test|chore|build|ci)/)
    n++
    typ[n] = substr(head, 1, RLENGTH)
    subj[n] = rest
    if (substr(head, length(head) - 2, 1) == "!") brk[n] = 1
    prev = n
    conv++
  }
  END {
    first = 1
    nsec = split("Features|feat|Bug Fixes|fix|Performance|perf|Refactoring|refactor|Documentation|docs", secs, "|")
    for (s = 1; s <= nsec; s += 2) {
      want = secs[s + 1]
      count = 0
      for (i = 1; i <= n; i++) if (typ[i] == want) count++
      if (count == 0) continue
      if (!first) print ""
      first = 0
      print "## " secs[s]
      for (i = 1; i <= n; i++) if (typ[i] == want) print "- " subj[i]
    }
    nbreak = 0
    for (i = 1; i <= n; i++) if (i in brk) nbreak++
    if (nbreak > 0) {
      if (!first) print ""
      first = 0
      print "## Breaking Changes"
      for (i = 1; i <= n; i++) if (i in brk) print "- " subj[i]
    }
    internal = 0; features = 0; fixes = 0
    for (i = 1; i <= n; i++) {
      if (typ[i] == "chore" || typ[i] == "build" || typ[i] == "ci" || typ[i] == "test") internal++
      if (typ[i] == "feat") features++
      if (typ[i] == "fix") fixes++
    }
    printf "%d %d %d %d %d %d %d\n", commits, conv, skipped, internal, nbreak, features, fixes > counts_out
  }
' counts_out="$scratch/counts.txt" "$source_file" > "$out_dir/changelog.md"

read -r n_commits n_conv n_skipped n_internal n_breaking n_features n_fixes < "$scratch/counts.txt"

jq -n \
  --argjson commits "$n_commits" \
  --argjson conventional "$n_conv" \
  --argjson skipped "$n_skipped" \
  --argjson internal "$n_internal" \
  --argjson breaking "$n_breaking" \
  --argjson features "$n_features" \
  --argjson fixes "$n_fixes" \
  '{commits: $commits, conventional: $conventional, skipped: $skipped, internal: $internal, breaking: $breaking, features: $features, fixes: $fixes}' \
  > "$out_dir/summary.json"
