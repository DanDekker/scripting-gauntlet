#!/usr/bin/env bash
# 201-bash-log-rotate — age in days needs a real day count, not field subtraction.
set -euo pipefail
export LC_ALL=C

IN="${IN:?IN not set}"
OUT="${OUT:?OUT not set}"

# Days since 1970-01-01 for a proleptic Gregorian date (Howard Hinnant's
# days_from_civil). Works in pure bash, so it does not depend on the flavour of
# `date` the host ships.
days_from_civil() {
  # 10# forces base 10: a date field like 08 is not an octal literal.
  local y=$(( 10#$1 )) m=$(( 10#$2 )) d=$(( 10#$3 )) era yoe doy doe
  if (( m <= 2 )); then
    y=$(( y - 1 ))
  fi
  era=$(( (y >= 0 ? y : y - 399) / 400 ))
  yoe=$(( y - era * 400 ))
  doy=$(( (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1 ))
  doe=$(( yoe * 365 + yoe / 4 - yoe / 100 + doy ))
  printf '%s\n' $(( era * 146097 + doe - 719468 ))
}

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
today_days=$(days_from_civil "$ty" "$tm" "$td")

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
    ly=${BASH_REMATCH[1]}
    lm=${BASH_REMATCH[2]}
    ld=${BASH_REMATCH[3]}
    age=$(( today_days - $(days_from_civil "$ly" "$lm" "$ld") ))
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
