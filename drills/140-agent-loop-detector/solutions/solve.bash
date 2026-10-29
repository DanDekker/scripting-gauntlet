#!/usr/bin/env bash
# Detect agent loops: canonicalize each action with jq, then scan greedily in awk.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -R 'fromjson? // empty | select(type == "object")
       | select((.step | type) == "number")
       | select((.tool | type) == "string")' "$in_dir/actions.jsonl" \
  | jq -r '
      def sortkeys:
        if type == "object"
        then (to_entries | sort_by(.key)
              | map({key: .key, value: (.value | sortkeys)}) | from_entries)
        elif type == "array" then map(sortkeys)
        else . end;
      "\(.step)\t\(.tool)\t\(.tool + ":" + (((.args // {}) | sortkeys) | tojson))"
    ' \
  | sort -s -n -k1,1 > "$scratch/actions.tsv"

total_steps=$(awk 'END { print NR + 0 }' "$scratch/actions.tsv")

awk -F'\t' '
  {
    n++
    step[n] = $1 + 0
    tool[n] = $2
    key[n] = $3
  }

  function report(start, end, kind, text) {
    printf "%d,%d,%s,%s\n", step[start], step[end], kind, text
  }

  END {
    i = 1
    while (i <= n) {
      # period 1: a run of identical consecutive actions
      j = i
      while (j + 1 <= n && key[j + 1] == key[i]) j++
      if (j - i + 1 >= 3) {
        report(i, j, "repeat_action", tool[i] " repeated " (j - i + 1) "x")
        i = j + 1
        continue
      }

      # period 2: longest span where action[m] == action[m + 2]
      j = i - 1
      m = i
      while (m + 2 <= n && key[m] == key[m + 2]) { j = m + 2; m++ }
      if (j - i + 1 >= 6) {
        report(i, j, "cycle_2", tool[i] " <-> " tool[i + 1] " x" int((j - i + 1) / 2))
        i = j + 1
        continue
      }

      # period 3: longest span where action[m] == action[m + 3]
      j = i - 1
      m = i
      while (m + 3 <= n && key[m] == key[m + 3]) { j = m + 3; m++ }
      if (j - i + 1 >= 6) {
        report(i, j, "cycle_3", tool[i] " -> " tool[i + 1] " -> " tool[i + 2] " x" int((j - i + 1) / 3))
        i = j + 1
        continue
      }

      i++
    }
  }
' "$scratch/actions.tsv" > "$scratch/loops.csv"

{
  printf 'start_step,end_step,pattern_type,description\n'
  cat "$scratch/loops.csv"
} > "$out_dir/loops.csv"

loop_count=$(awk 'END { print NR + 0 }' "$scratch/loops.csv")
if [ "$loop_count" -eq 0 ]; then
  first_loop_step=null
else
  first_loop_step=$(head -n 1 "$scratch/loops.csv" | cut -d, -f1)
fi

jq -n \
  --argjson total_steps "$total_steps" \
  --argjson loop_count "$loop_count" \
  --argjson first_loop_step "$first_loop_step" \
  '{total_steps: $total_steps,
    status: (if $loop_count > 0 then "looping" else "healthy" end),
    loop_count: $loop_count,
    first_loop_step: $first_loop_step}' > "$out_dir/summary.json"
