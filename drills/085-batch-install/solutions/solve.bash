#!/usr/bin/env bash
# 085-batch-install - validate the whole batch, back up, then rename into place.
set -euo pipefail
export LC_ALL=C

inp="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
work="${WORK:?WORK not set}"
target="$outdir/target"
mkdir -p "$target"
cp -R "$inp/target/." "$target/"

first_bad() {
  awk '
    /^[[:space:]]*$/ || /^[[:space:]]*#/ { next }
    $0 !~ /^[a-z_][a-z0-9_]*=/ { print FNR; exit 1 }
  ' "$1"
}

validate_batch() {
  local dir=$1 file line
  for file in "$dir"/*; do
    [[ -f "$file" ]] || continue
    if ! line=$(first_bad "$file"); then
      printf '%s:%s\n' "${file##*/}" "$line"
      return 1
    fi
  done
  return 0
}

install_batch() {
  local batch=$1 dir="$inp/$1" file name tmp backup
  backup="$work/backup-$batch"
  rm -rf "$backup"
  mkdir -p "$backup"
  cp -R "$target/." "$backup/" || return 1
  for file in "$dir"/*; do
    [[ -f "$file" ]] || continue
    name=${file##*/}
    tmp="$target/.$name.tmp"
    if ! cp "$file" "$tmp" || ! mv "$tmp" "$target/$name"; then
      rm -rf "$target"
      mkdir -p "$target"
      cp -R "$backup/." "$target/"
      return 1
    fi
  done
  return 0
}

applied=0
rejected=0
for batch in batch-a batch-b; do
  if bad=$(validate_batch "$inp/$batch"); then
    install_batch "$batch" || { echo "install failed: $batch" >&2; exit 1; }
    for file in "$inp/$batch"/*; do
      [[ -f "$file" ]] || continue
      applied=$((applied + 1))
    done
  else
    printf 'rejected %s/%s\n' "$batch" "$bad" >> "$outdir/reject.log"
    rejected=$((rejected + 1))
  fi
done

total=$(find "$target" -maxdepth 1 -type f | wc -l | tr -d ' ')
printf '{"applied_files":%d,"kept_files":%d,"total_files":%d,"rejected_batches":%d}\n' \
  "$applied" "$((total - applied))" "$total" "$rejected" > "$outdir/summary.json"
