#!/usr/bin/env bash
# Fold continuation lines and collect the handoff with awk, then assemble JSON with jq.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

src="$in_dir/session.log"
[ -f "$src" ] || { printf 'missing %s\n' "$src" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

awk '
function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
{
  if ($0 ~ /^[ \t]/) {
    t = trim($0)
    if (n == 0 || t == "") next
    line[n] = line[n] " " t
    next
  }
  n++
  line[n] = $0
}
END {
  for (i = 1; i <= n; i++) {
    t = trim(line[i])
    if (t == "") continue
    if (t ~ /^USER:/) { printf "R\t%s\n", trim(substr(t, 6)); continue }
    split(t, head, /[ \t]+/)
    if (head[1] == "TOOL" && head[2] != "") {
      printf "C\t%s\n", head[2]
      if (!(head[2] in seen)) { seen[head[2]] = 1; printf "T\t%s\n", head[2] }
      continue
    }
    if (head[1] == "RESULT") {
      rest = substr(t, 7)
      ci = index(rest, ":")
      if (ci > 0) printf "S\t%s\n", trim(substr(rest, 1, ci - 1))
      continue
    }
    if (t ~ /^NOTE:/) { printf "N\t%s\n", trim(substr(t, 6)); continue }
    if (t ~ /^ERROR:/) { printf "E\t%s\n", trim(substr(t, 7)); continue }
  }
}
' "$src" > "$scratch/events.txt"

jq -R -s '
  [split("\n")[] | select(length > 0) | split("\t")] as $rows
  | ($rows | map(select(.[0] == "S")) | map(.[1])) as $resnames
  | ($rows | map(select(.[0] == "C")) | map(.[1])) as $callnames
  | {request: ($rows | map(select(.[0] == "R")) | if length == 0 then "" else .[-1][1] end),
     tools: ($rows | map(select(.[0] == "T")) | map(.[1])),
     results: ($resnames | length),
     notes: ($rows | map(select(.[0] == "N")) | map(.[1])),
     errors: ($rows | map(select(.[0] == "E")) | map(.[1])),
     calls: ($callnames | length),
     unresolved: ([$callnames[] as $n | select(($resnames | index($n)) == null)] | length)}
' "$scratch/events.txt" > "$out_dir/handoff.json"
