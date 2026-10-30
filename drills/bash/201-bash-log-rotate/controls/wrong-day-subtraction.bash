#!/usr/bin/env bash
# Plausible bug: age computed by subtracting the day-of-month only, so any log
# from an earlier month or year comes out far too young.
set -euo pipefail
export LC_ALL=C

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

policy_get() {
  local key=$1 line
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == "$key="* ]]; then
      printf '%s\n' "${line#*=}"
      return 0
    fi
  done < "$IN/policy.txt"
  printf 'policy.txt: missing key %s\n' "$key" >&2
  exit 1
}

today=$(policy_get today)
compress_after=$(policy_get compress_after_days)
delete_after=$(policy_get delete_after_days)

IFS='-' read -r ty tm td <<< "$today"

mkdir -p "$OUT/logs"

rows=()
kept=0
compressed=0
deleted=0
ignored=0

shopt -s nullglob
for src in "$IN"/logs/*; do
  [[ -f "$src" ]] || continue
  base=${src##*/}
  if [[ "$base" =~ ^svc-([0-9]{4})-([0-9]{2})-([0-9]{2})\.log$ ]]; then
    ld=$(( 10#${BASH_REMATCH[3]} ))
    # BUG: day-of-month subtraction ignores months and years entirely.
    age=$(( td - ld ))
    if (( age >= delete_after )); then
      action=delete
      deleted=$(( deleted + 1 ))
    elif (( age >= compress_after )); then
      action=compress
      compressed=$(( compressed + 1 ))
    else
      action=keep
      kept=$(( kept + 1 ))
    fi
    rows+=("$base,$age,$action")
    case "$action" in
      keep) cp "$src" "$OUT/logs/$base" ;;
      compress) gzip -c "$src" > "$OUT/logs/$base.gz" ;;
      delete) : ;;
    esac
  else
    ignored=$(( ignored + 1 ))
  fi
done

{
  printf 'file,age_days,action\n'
  if (( ${#rows[@]} > 0 )); then
    printf '%s\n' "${rows[@]}" | sort
  fi
} > "$OUT/rotation.csv"

printf '{"kept":%d,"compressed":%d,"deleted":%d,"ignored":%d}\n' \
  "$kept" "$compressed" "$deleted" "$ignored" > "$OUT/summary.json"
