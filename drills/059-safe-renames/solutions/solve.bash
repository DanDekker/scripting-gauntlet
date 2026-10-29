#!/usr/bin/env bash
set -euo pipefail

source_tree="${IN:?IN not set}/tree"
plan="$IN/renames.tsv"
tree="${OUT:?OUT not set}/tree"
stage="${WORK:?WORK not set}/staged-renames"
[[ -d "$source_tree" && -f "$plan" ]] || { echo "missing tree or plan" >&2; exit 1; }
cp -R "$source_tree" "$tree"
mkdir -p "$stage"

froms=()
tos=()
while IFS=$'\t' read -r from to extra || [[ -n "${from:-}" ]]; do
  [[ -z "$from" || "$from" == \#* ]] && continue
  [[ -n "${to:-}" && -z "${extra:-}" ]] || { echo "bad plan row: $from" >&2; exit 1; }
  [[ "$from" != */* && "$to" != */* && "$from" != "$to" ]] || { echo "bad rename: $from -> $to" >&2; exit 1; }
  [[ -f "$tree/$from" && ! -L "$tree/$from" ]] || { echo "missing source: $from" >&2; exit 1; }
  for old in "${froms[@]:-}"; do
    [[ "$old" != "$from" ]] || { echo "duplicate source: $from" >&2; exit 1; }
  done
  for old in "${tos[@]:-}"; do
    [[ "$old" != "$to" ]] || { echo "duplicate destination: $to" >&2; exit 1; }
  done
  froms+=("$from")
  tos+=("$to")
done < "$plan"

for to in "${tos[@]}"; do
  [[ ! -e "$tree/$to" ]] && continue
  allowed=0
  for from in "${froms[@]}"; do
    [[ "$to" == "$from" ]] && allowed=1
  done
  [[ "$allowed" -eq 1 ]] || { echo "destination exists: $to" >&2; exit 1; }
done

for i in "${!froms[@]}"; do
  mv "$tree/${froms[i]}" "$stage/$i"
done
for i in "${!tos[@]}"; do
  mv "$stage/$i" "$tree/${tos[i]}"
done

{
  printf 'from,to\n'
  for i in "${!froms[@]}"; do printf '%s,%s\n' "${froms[i]}" "${tos[i]}"; done | LC_ALL=C sort
} > "$OUT/moves.csv"
total=$(find "$source_tree" -type f -print | wc -l | tr -d ' ')
printf '{"moved":%d,"untouched":%d}\n' "${#froms[@]}" "$((total - ${#froms[@]}))" > "$OUT/summary.json"
