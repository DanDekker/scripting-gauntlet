#!/usr/bin/env bash
# 086-fuzzy-find - find, filter, score, sort, then read only the winner.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
hint="$inp/hint.txt"
tree="$inp/tree"
home="$tree/home/pp"
mkdir -p "$outdir"
[[ -r "$hint" ]] || { echo "missing $hint" >&2; exit 1; }

trim() {
  local s=$1
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

keywords=()
extension=""
max_size=0
roots=()
while IFS= read -r line; do
  line=$(trim "$line")
  [[ -z "$line" || "$line" == \#* ]] && continue
  key=$(trim "${line%%:*}")
  value=$(trim "${line#*:}")
  case "$key" in
    keywords) IFS=',' read -r -a parts <<< "$value"
              for part in "${parts[@]}"; do keywords+=("$(trim "$part")"); done ;;
    extension) extension=$(printf '%s' "$value" | tr '[:upper:]' '[:lower:]') ;;
    max_size) max_size=$value ;;
    roots) read -r -a roots <<< "$value" ;;
    *) echo "unknown hint key: $key" >&2; exit 1 ;;
  esac
done < "$hint"
[[ ${#keywords[@]} -gt 0 && -n "$extension" && ${#roots[@]} -gt 0 ]] \
  || { echo "incomplete hint" >&2; exit 1; }

mtime_of() {
  if stat -c '%Y' "$1" >/dev/null 2>&1; then stat -c '%Y' "$1"; else stat -f '%m' "$1"; fi
}

scanned=0
rows=$(mktemp)
trap 'rm -f "$rows"' EXIT
for root in "${roots[@]}"; do
  start="$home/$root"
  [[ -d "$start" ]] || { echo "missing root: $start" >&2; exit 1; }
  while IFS= read -r -d '' file; do
    scanned=$((scanned + 1))
    base=${file##*/}
    lower=$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')
    [[ "${lower##*.}" == "$extension" ]] || continue
    size=$(wc -c < "$file" | tr -d ' ')
    (( size <= max_size )) || continue
    score=0
    for word in "${keywords[@]}"; do
      word_lower=$(printf '%s' "$word" | tr '[:upper:]' '[:lower:]')
      [[ "$lower" == *"$word_lower"* ]] && score=$((score + 1))
    done
    (( score >= 2 )) || continue
    printf '%s\t%d\t%s\n' "${file#"$tree/"}" "$score" "$(mtime_of "$file")" >> "$rows"
  done < <(find "$start" -type f ! -path '*/.*' -print0)
done

LC_ALL=C sort -t$'\t' -k2,2nr -k3,3nr -k1,1 "$rows" > "$rows.sorted"
trap 'rm -f "$rows" "$rows.sorted"' EXIT

{
  printf 'path,score\n'
  awk -F'\t' '{ printf "%s,%s\n", $1, $2 }' "$rows.sorted"
} > "$outdir/candidates.csv"

count=$(awk 'END { print NR }' "$rows.sorted")
(( count > 0 )) || { echo "no candidates matched the hint" >&2; exit 1; }

winner=$(awk -F'\t' 'NR == 1 { print $1 }' "$rows.sorted")
score=$(awk -F'\t' 'NR == 1 { print $2 }' "$rows.sorted")
read -r data_rows total < <(awk -F',' '
  NR == 1 { if (tolower($1) != "month" || tolower($2) != "amount") exit 1; next }
  $1 == "" { next }
  { n++; sum += $2 }
  END { printf "%d %.2f\n", n, sum }
' "$tree/$winner") || { echo "cannot read $tree/$winner" >&2; exit 1; }

printf '{"path":"%s","score":%d,"rows":%d,"total":%s}\n' \
  "$winner" "$score" "$data_rows" "$total" > "$outdir/found.json"
printf '{"scanned":%d,"candidates":%d}\n' "$scanned" "$count" > "$outdir/summary.json"
