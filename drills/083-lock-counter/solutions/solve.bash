#!/usr/bin/env bash
# 083-lock-counter - mkdir is the atomic primitive; every read happens inside the lock.
set -euo pipefail

export LC_ALL=C
outdir="${OUT:?OUT not set}"
work="${WORK:?WORK not set}"
mkdir -p "$outdir"

counter="$outdir/counter.txt"
events="$outdir/events.log"
lock="$work/counter.lock"
workers=4
per_worker=50

printf '0\n' > "$counter"
: > "$events"

acquire() {
  local tries=0
  while ! mkdir "$lock" 2>/dev/null; do
    tries=$((tries + 1))
    (( tries < 2000 )) || { echo "lock timeout" >&2; return 1; }
    sleep 0.01
  done
}

release() { rmdir "$lock"; }

worker() {
  local id=$1 n=0 current
  while (( n < per_worker )); do
    acquire || exit 1
    current=$(tr -d '[:space:]' < "$counter")
    printf '%d\n' "$((current + 1))" > "$counter"
    printf '%d\n' "$id" >> "$events"
    release
    n=$((n + 1))
  done
}

pids=()
for id in 0 1 2 3; do
  worker "$id" &
  pids+=("$!")
 done
for pid in "${pids[@]}"; do
  wait "$pid" || { echo "worker $pid failed" >&2; exit 1; }
done

rmdir "$lock" 2>/dev/null || true
printf '{"workers":%d,"per_worker":%d,"total":%d}\n' \
  "$workers" "$per_worker" "$((workers * per_worker))" > "$outdir/summary.json"
