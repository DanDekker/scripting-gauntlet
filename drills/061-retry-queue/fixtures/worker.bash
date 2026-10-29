#!/usr/bin/env bash
set -euo pipefail

job=${1:?job missing}
state=${2:?state directory missing}
mkdir -p "$state"
count_file="$state/$job"
count=0
if [[ -f "$count_file" ]]; then count=$(cat "$count_file"); fi
count=$((count + 1))
printf '%d\n' "$count" > "$count_file"

case "$job" in
  steady) echo ready ;;
  flaky)
    if [[ "$count" -lt 3 ]]; then echo busy >&2; exit 75; fi
    echo recovered ;;
  permanent) echo 'bad config' >&2; exit 2 ;;
  once)
    if [[ "$count" -lt 2 ]]; then echo busy >&2; exit 75; fi
    echo warmed ;;
  exhausted) echo busy >&2; exit 75 ;;
  *) echo "unknown job: $job" >&2; exit 64 ;;
esac
