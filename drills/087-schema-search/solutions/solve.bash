#!/usr/bin/env bash
# 087-schema-search - header parsed once per file, rows counted only on a match.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
dump="$inp/dump"
mkdir -p "$outdir"
[[ -d "$dump" ]] || { echo "missing $dump" >&2; exit 1; }

want=$(sed -n 's/^columns:[[:space:]]*//p' "$inp/hint.txt" | tr ',' ' ' | tr -s '[:space:]' ' ')
want=$(printf '%s' "$want" | sed 's/^ //; s/ $//')
[[ -n "$want" ]] || { echo "hint names no columns" >&2; exit 1; }

scanned=0
rows=$(mktemp)
trap 'rm -f "$rows"' EXIT

while IFS= read -r -d '' file; do
  scanned=$((scanned + 1))
  base=${file##*/}
  ext=${base##*.}
  case "$ext" in
    csv) d=','; dname=comma ;;
    tsv) d=$'\t'; dname=tab ;;
    *) continue ;;
  esac
  result=$(sed $'1s/^\xef\xbb\xbf//' "$file" | awk -v want="$want" -v d="$d" '
    BEGIN { FS = d; n = split(want, W, " "); ok = 1 }
    NR == 1 {
      cols = split($0, H, d)
      for (j = 1; j <= n; j++) seen[j] = 0
      for (i = 1; i <= cols; i++) {
        h = tolower(H[i]); sub(/^[ \t"]+/, "", h); sub(/[ \t"]+$/, "", h)
        if (h == "budget") budget = i
        for (j = 1; j <= n; j++) if (h == W[j]) seen[j] = 1
      }
      for (j = 1; j <= n; j++) if (!seen[j]) { ok = 0; exit }
      if (!budget) { ok = 0; exit }
      next
    }
    { if ($0 !~ /^[ \t]*$/) { rows++; sum += $(budget) } }
    END {
      if (!ok || NR == 0) exit 1
      printf "%d %d %.2f\n", cols, rows, sum
    }' 2>/dev/null) || continue
  read -r cols data_rows total <<< "$result"
  printf '%s\t%s\t%s\t%s\t%s\n' "${file#"$dump/"}" "$dname" "$cols" "$data_rows" "$total" \
    >> "$rows"
done < <(find "$dump" -type f ! -path '*/.*' -name '*.csv' -print0
         find "$dump" -type f ! -path '*/.*' -name '*.tsv' -print0)

LC_ALL=C sort -t$'\t' -k1,1 "$rows" > "$rows.sorted"
trap 'rm -f "$rows" "$rows.sorted"' EXIT

{
  printf 'path,delimiter,columns,rows\n'
  awk -F'\t' '{ printf "%s,%s,%s,%s\n", $1, $2, $3, $4 }' "$rows.sorted"
} > "$outdir/matches.csv"

count=$(awk 'END { print NR }' "$rows.sorted")
printf '{"files_scanned":%d,"matches":%d}\n' "$scanned" "$count" > "$outdir/summary.json"
(( count > 0 )) || { echo "no table has all the wanted columns" >&2; exit 1; }

best=$(LC_ALL=C sort -t$'\t' -k4,4nr -k1,1 "$rows.sorted" | head -1)
bestpath=${best%%$'\t'*}
rest=${best#*$'\t'}
IFS=$'\t' read -r _delim _cols best_rows best_total <<< "$rest"
printf '{"path":"%s","rows":%s,"total":%s}\n' "$bestpath" "$best_rows" "$best_total" \
  > "$outdir/found.json"
