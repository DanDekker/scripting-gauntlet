#!/usr/bin/env bash
# 076-runaway-files - find never follows links; stat both flavours, dedupe by inode.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
tree="$inp/tree"
[[ -d "$tree" ]] || { echo "missing $tree" >&2; exit 1; }
mkdir -p "$outdir"

if stat -c '%i %s' / >/dev/null 2>&1; then
  stat_args=(-c '%i %s')
else
  stat_args=(-f '%i %z')
fi

rows=$(mktemp)
trap 'rm -f "$rows"' EXIT

ignored=0
links=0
declare -A size_of=()
declare -A path_of=()
while IFS= read -r -d '' file; do
  read -r inode size < <(stat "${stat_args[@]}" "$file")
  rel=${file#"$tree"/}
  if [[ -n "${path_of[$inode]:-}" ]]; then
    links=$((links + 1))
    if [[ "$rel" < "${path_of[$inode]}" ]]; then
      path_of[$inode]=$rel
      size_of[$inode]=$size
    fi
    continue
  fi
  path_of[$inode]=$rel
  size_of[$inode]=$size
done < <(find "$tree" -type f -print0)

for inode in "${!path_of[@]}"; do
  rel=${path_of[$inode]}
  size=${size_of[$inode]}
  case "/$rel/" in
    */node_modules/*|*/.cache/*|*/__pycache__/*) ignored=$((ignored + size)); continue ;;
  esac
  printf '%s\t%s\n' "$size" "$rel" >> "$rows"
done
files=$(awk 'END { print NR }' "$rows")

bytes=$(awk -F'\t' '{ total += $1 } END { print total + 0 }' "$rows")

{
  printf 'rank,path,size_mb\n'
  LC_ALL=C sort -t$'\t' -k1,1nr -k2,2 "$rows" | head -n 5 | awk -F'\t' -v rank=0 '
    { rank++; printf "%d,%s,%.2f\n", rank, $2, $1 / 1048576 }'
} > "$outdir/top_files.csv"

printf '{"files":%d,"bytes":%d,"ignored_bytes":%d,"links_skipped":%d}\n' \
  "$files" "$bytes" "$ignored" "$links" > "$outdir/summary.json"
