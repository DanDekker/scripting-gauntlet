#!/usr/bin/env bash
# Catalogue merge-conflict blocks with one awk state machine per file.
set -euo pipefail

export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

root="$in_dir/repo"
find "$root" -type f > "$scratch/files.txt"
scanned=$(wc -l < "$scratch/files.txt" | tr -d ' ')

: > "$scratch/rows.tsv"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  rel=${path#"$root"/}
  awk -v file="$rel" -v out="$scratch/rows.tsv" '
    function trim(s) { gsub(/^[ \t\r]+/, "", s); gsub(/[ \t\r]+$/, "", s); return s }
    {
      line = $0
      sub(/\r$/, "", line)
      if (line ~ /^<<<<<<< /) {
        state = 1; start = FNR
        ours = trim(substr(line, 9)); ourn = 0; theirn = 0
        next
      }
      if (state == 1) {
        if (line ~ /^\|\|\|\|\|\|\| /) { state = 2; next }
        if (line ~ /^=======[ \t]*$/) { state = 3; next }
        ourn++; next
      }
      if (state == 2) {
        if (line ~ /^=======[ \t]*$/) { state = 3 }
        next
      }
      if (state == 3) {
        if (line ~ /^>>>>>>> /) {
          printf "%s\t%d\t%d\t%s\t%s\t%d\t%d\n", file, start, FNR, ours, trim(substr(line, 9)), ourn, theirn >> out
          state = 0; next
        }
        theirn++; next
      }
    }
  ' "$path"
done < "$scratch/files.txt"

{
  printf 'file,start_line,end_line,our_branch,their_branch,our_lines,their_lines\n'
  sort -t"$(printf '\t')" -k1,1 -k2,2n "$scratch/rows.tsv" \
    | awk -F'\t' '{ printf "%s,%s,%s,%s,%s,%s,%s\n", $1, $2, $3, $4, $5, $6, $7 }'
} > "$out_dir/conflicts.csv"

total=$(wc -l < "$scratch/rows.tsv" | tr -d ' ')
conflicted=$(cut -f1 "$scratch/rows.tsv" | sort -u | wc -l | tr -d ' ')
widest=$(awk -F'\t' '{ n = $6 + $7; if (n > m) m = n } END { print m + 0 }' "$scratch/rows.tsv")
clean=$((scanned - conflicted))

jq -n \
  --argjson scanned "$scanned" \
  --argjson conflicted "$conflicted" \
  --argjson total "$total" \
  --argjson clean "$clean" \
  --argjson widest "$widest" \
  '{files_scanned: $scanned, conflicted_files: $conflicted, total_conflicts: $total,
    clean_files: $clean, max_conflict_lines: $widest}' > "$out_dir/summary.json"
