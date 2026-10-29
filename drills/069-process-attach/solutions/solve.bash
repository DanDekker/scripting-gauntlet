#!/usr/bin/env bash
set -euo pipefail

if command -v python3 >/dev/null; then py=(python3)
elif command -v python >/dev/null; then py=(python)
elif command -v py >/dev/null; then py=(py -3)
else echo "need Python 3" >&2; exit 1
fi
ready="$WORK/ready.json"
stop="$WORK/stop.flag"
heartbeat="$WORK/heartbeat.txt"
pid=
cleanup() {
  [[ -n "$pid" ]] || return 0
  : > "$stop"
  for ((i=0; i<40; i++)); do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.05
  done
  if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; fi
  wait "$pid" 2>/dev/null || true
}
"${py[@]}" "$IN/worker.py" "$ready" "$stop" "$heartbeat" >/dev/null 2>&1 &
pid=$!
trap cleanup EXIT

for ((i=0; i<100; i++)); do
  [[ -s "$ready" ]] && break
  kill -0 "$pid" 2>/dev/null || { echo "worker exited before ready" >&2; exit 1; }
  sleep 0.05
done
[[ -s "$ready" ]] || { echo "worker readiness timed out" >&2; exit 1; }
ready_pid=$(jq -er '.pid' "$ready")
port=$(jq -er '.port' "$ready")
[[ "$ready_pid" == "$pid" ]] || { echo "worker PID mismatch" >&2; exit 1; }
attached=$(ps -p "$ready_pid" -o pid= | tr -d '[:space:]')
[[ "$attached" == "$pid" ]] || { echo "cannot attach to PID $pid" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
health=$(curl --fail --silent --show-error --connect-timeout 1 --max-time 2 \
  "http://127.0.0.1:$port/health") || { echo "listener probe failed on port $port" >&2; exit 1; }
[[ "$health" == ready ]] || { echo "unexpected listener response: $health" >&2; exit 1; }
before=$(cat "$heartbeat")
sleep 0.12
after=$(cat "$heartbeat")
[[ "$after" -gt "$before" ]] || { echo "heartbeat did not advance" >&2; exit 1; }

: > "$stop"
wait "$pid" || { echo "worker did not stop cleanly" >&2; exit 1; }
if kill -0 "$pid" 2>/dev/null; then
  echo "worker still running" >&2
  exit 1
fi
trap - EXIT
printf '{"pid":%d,"ready_pid":%d,"port":%d,"heartbeat_before":%d,"heartbeat_after":%d,"attached":true,"listener_ok":true,"stopped":true}\n' \
  "$pid" "$ready_pid" "$port" "$before" "$after" > "$OUT/attachment.json"
