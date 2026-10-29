#!/usr/bin/env bash
set -euo pipefail

queue="${IN:?IN not set}/jobs.txt"
worker="$IN/worker.bash"
out="${OUT:?OUT not set}"
work="${WORK:?WORK not set}"
state="$work/attempt-state"
[[ -f "$queue" && -f "$worker" ]] || { echo "missing queue or worker" >&2; exit 1; }
mkdir -p "$state"
printf 'job,attempt,exit_code\n' > "$out/attempts.csv"
printf 'job,status,attempts,message\n' > "$out/results.csv"

jobs=0
ok=0
failed=0
attempts=0
while IFS= read -r job || [[ -n "$job" ]]; do
  [[ -z "$job" || "$job" == \#* ]] && continue
  [[ "$job" =~ ^[a-z]+$ ]] || { echo "bad job: $job" >&2; exit 1; }
  jobs=$((jobs + 1))
  status=failed
  message=
  for attempt in 1 2 3; do
    if bash "$worker" "$job" "$state" > "$work/stdout" 2> "$work/stderr"; then
      code=0
    else
      code=$?
    fi
    printf '%s,%d,%d\n' "$job" "$attempt" "$code" >> "$out/attempts.csv"
    attempts=$((attempts + 1))
    if [[ "$code" -eq 0 ]]; then
      status=ok
      message=$(cat "$work/stdout")
      break
    fi
    message=$(cat "$work/stderr")
    [[ "$code" -eq 75 ]] || break
  done
  if [[ "$status" == ok ]]; then ok=$((ok + 1)); else failed=$((failed + 1)); fi
  printf '%s,%s,%d,%s\n' "$job" "$status" "$attempt" "$message" >> "$out/results.csv"
done < "$queue"

printf '{"jobs":%d,"ok":%d,"failed":%d,"attempts":%d}\n' \
  "$jobs" "$ok" "$failed" "$attempts" > "$out/summary.json"
