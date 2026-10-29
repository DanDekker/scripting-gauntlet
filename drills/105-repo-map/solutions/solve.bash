#!/usr/bin/env bash
# Repo map with find + awk: prune the skip list, then bucket by kind and top dir.
set -euo pipefail
export LC_ALL=C

in_dir="$IN"
out_dir="$OUT"
mkdir -p "$out_dir"

tree="$in_dir/tree"
[ -d "$tree" ] || { echo "missing input tree: $tree" >&2; exit 1; }

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

: > "$scratch/files.tsv"
: > "$scratch/skipped.txt"

find "$tree" \
  \( -name node_modules -o -name __pycache__ -o -name .git -o -name dist \) -prune -o \
  -type f -print0 |
while IFS= read -r -d '' path; do
  rel=${path#"$tree"/}
  base=${rel##*/}
  case $base in
    .*) printf '%s\n' "$rel" >> "$scratch/skipped.txt"; continue ;;
  esac
  size=$(wc -c < "$path")
  size=${size// /}
  printf '%s\t%s\n' "$rel" "$size" >> "$scratch/files.tsv"
done

awk -F'\t' '
  {
    rel = $1; size = $2
    n = split(rel, parts, "/")
    base = parts[n]
    top = (n > 1) ? parts[1] : "(root)"

    dot = 0
    for (i = length(base); i > 0; i--) if (substr(base, i, 1) == ".") { dot = i; break }
    stem = (dot > 1) ? substr(base, 1, dot - 1) : base
    ext = (dot > 0) ? tolower(substr(base, dot + 1)) : ""

    if (stem ~ /\.test$/ || stem ~ /_test$/) kind = "test"
    else if (base == "package.json" || base == "Makefile" || base == "pyproject.toml" || base == "setup.cfg" || base == "tsconfig.json") kind = "config"
    else if (ext == "py") kind = "py"
    else if (ext == "js" || ext == "mjs" || ext == "cjs") kind = "js"
    else if (ext == "ts" || ext == "tsx") kind = "ts"
    else if (ext == "md") kind = "md"
    else kind = "other"

    kcount[kind]++
    kbytes[kind] += size
    dcount[top]++
    files++
    bytes += size
    if (size > largest) largest = size
  }
  END {
    for (k in kcount) printf "%s,%d,%d\n", k, kcount[k], kbytes[k] > kinds_out
    for (d in dcount) printf "%s,%d\n", d, dcount[d] > dirs_out
    printf "%d %d %d\n", files + 0, bytes + 0, largest + 0 > totals_out
  }
' kinds_out="$scratch/kinds.csv" dirs_out="$scratch/dirs.csv" totals_out="$scratch/totals.txt" \
  "$scratch/files.tsv"

n_dirs=$(wc -l < "$scratch/dirs.csv")
n_dirs=${n_dirs// /}
n_skipped=$(wc -l < "$scratch/skipped.txt")
n_skipped=${n_skipped// /}
read -r n_files n_bytes n_largest < "$scratch/totals.txt"

{
  printf 'kind,files,bytes\n'
  sort "$scratch/kinds.csv"
} > "$out_dir/map.csv"

{
  printf 'dir,files\n'
  sort "$scratch/dirs.csv"
} > "$out_dir/dirs.csv"

jq -n \
  --argjson files "$n_files" \
  --argjson bytes "$n_bytes" \
  --argjson skipped "$n_skipped" \
  --argjson dirs "$n_dirs" \
  --argjson largest "$n_largest" \
  '{files: $files, bytes: $bytes, skipped: $skipped, dirs: $dirs, largest: $largest}' \
  > "$out_dir/summary.json"
