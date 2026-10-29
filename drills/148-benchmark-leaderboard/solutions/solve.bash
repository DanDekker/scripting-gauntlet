#!/usr/bin/env bash
# Weighted benchmark leaderboard: jq reads the suite config, awk does the arithmetic, sort
# does the ranking.
set -euo pipefail

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

jq -r 'to_entries[]
       | [.key, (.value.weight // 0),
          (if .value.higher_is_better == false then "false" else "true" end)]
       | @tsv' "$in_dir/weights.json" > "$scratch/weights.tsv"

tail -n +2 "$in_dir/results.csv" | awk -F, '
  function trim(s) { gsub(/^[ \t\r]+/, "", s); gsub(/[ \t\r]+$/, "", s); return s }
  {
    if (trim($0) == "") next
    if (NF < 4) next
    m = trim($1); s = trim($2); v = trim($3)
    if (m == "" || s == "") next
    print m "\t" s "\t" v
  }
' > "$scratch/results.tsv"

awk -F'\t' -v board="$scratch/board.txt" '
  NR == FNR {
    w[$1] = $2 + 0
    hib[$1] = ($3 == "true")
    order[++ns] = $1
    totw += $2 + 0
    next
  }
  {
    m = $1; s = $2; v = $3
    if (!(m in MODELS)) { MODELS[m] = 1; MODLIST[++nm] = m }
    if (!(s in w)) next
    if (v ~ /^[-+]?([0-9]+\.?[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?$/) {
      SCORE[m, s] = v + 0; VALID[m, s] = 1
    } else {
      delete SCORE[m, s]; VALID[m, s] = 0
    }
  }
  END {
    for (i = 1; i <= ns; i++) {
      s = order[i]; first = 1
      for (j = 1; j <= nm; j++) {
        m = MODLIST[j]
        if (VALID[m, s] != 1) continue
        x = SCORE[m, s]
        if (first) { mn[s] = x; mx[s] = x; first = 0 }
        else { if (x < mn[s]) mn[s] = x; if (x > mx[s]) mx[s] = x }
      }
    }
    complete = 0
    for (j = 1; j <= nm; j++) {
      m = MODLIST[j]; is_complete = 1
      for (i = 1; i <= ns; i++) if (VALID[m, order[i]] != 1) is_complete = 0
      if (!is_complete) continue
      complete++
      sum = 0
      for (i = 1; i <= ns; i++) {
        s = order[i]; x = SCORE[m, s]
        if (mx[s] == mn[s]) norm = 1.0
        else if (hib[s]) norm = (x - mn[s]) / (mx[s] - mn[s])
        else norm = (mx[s] - x) / (mx[s] - mn[s])
        sum += norm * w[s]
      }
      comp = (totw == 0 ? 0 : sum / totw)
      printf "%.4f\t%s\n", comp, m > board
    }
    printf "%d\t%d\n", nm, complete > (board ".counts")
  }
' "$scratch/weights.tsv" "$scratch/results.tsv"

LC_ALL=C sort -t$'\t' -k1,1nr -k2,2 "$scratch/board.txt" > "$scratch/ranked.txt"

{
  printf 'rank,model,composite_score\n'
  awk -F'\t' '{ printf "%d,%s,%s\n", NR, $2, $1 }' "$scratch/ranked.txt"
} > "$out_dir/leaderboard.csv"

read -r total_models complete_models < "$scratch/board.txt.counts"
top_model=""
winning_score="0.0000"
if [ -s "$scratch/ranked.txt" ]; then
  winning_score=$(cut -f1 "$scratch/ranked.txt" | head -1)
  top_model=$(cut -f2 "$scratch/ranked.txt" | head -1)
fi

jq -n \
  --argjson total_models "$total_models" \
  --argjson complete_models "$complete_models" \
  --arg top_model "$top_model" \
  --argjson winning_score "$winning_score" \
  '{total_models: $total_models, complete_models: $complete_models,
    incomplete_models: ($total_models - $complete_models),
    top_model: $top_model, winning_score: $winning_score}' > "$out_dir/summary.json"
