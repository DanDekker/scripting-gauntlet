#!/usr/bin/env bash
# 055-localport-scan — a refused connect on loopback is instant; no long timeout needed.
set -euo pipefail

outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

scanned=0
for port in $(seq 46000 46010); do
  scanned=$((scanned + 1))
  if (exec 3<>/dev/tcp/127.0.0.1/"$port") 2>/dev/null; then
    exec 3<&- 2>/dev/null || true
    exec 3>&- 2>/dev/null || true
    printf '%s\n' "$port" >> "$body"
  fi
done

{
  printf 'port\n'
  sort -n "$body"
} > "$outdir/open_ports.csv"

open=$(wc -l < "$body" | tr -d ' ')
printf '{"scanned":%d,"open":%d}\n' "$scanned" "$open" > "$outdir/summary.json"
