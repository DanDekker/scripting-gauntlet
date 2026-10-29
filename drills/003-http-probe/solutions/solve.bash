#!/usr/bin/env bash
# 003-http-probe — curl + jq, follow the next link, cap the loop.
set -euo pipefail

base="${API_BASE:?API_BASE not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

health=$(curl -fsS "$base/health") || { echo "health request failed" >&2; exit 1; }
ok=$(printf '%s' "$health" | jq -r '.ok')
version=$(printf '%s' "$health" | jq -r '.version')
if [ "$ok" != "true" ]; then
  echo "service reports unhealthy: $health" >&2
  exit 1
fi

collected=$(mktemp)
trap 'rm -f "$collected"' EXIT

next="/api/v1/items?page=1"
visited=" "
pages=0
while [ -n "$next" ] && [ "$next" != "null" ]; do
  case "$visited" in
    *" $next "*) echo "pagination loop at $next" >&2; exit 1 ;;
  esac
  visited="$visited$next "

  pages=$((pages + 1))
  if [ "$pages" -gt 50 ]; then
    echo "exceeded 50 pages" >&2
    exit 1
  fi

  body=$(curl -fsS "$base$next") || { echo "request failed: $next" >&2; exit 1; }
  printf '%s' "$body" | jq -c '.items[]' >> "$collected"
  next=$(printf '%s' "$body" | jq -r '.next // empty')
done

jq -s 'sort_by(.id)' "$collected" > "$outdir/items.json"
count=$(jq 'length' "$outdir/items.json")

jq -n \
  --argjson ok "$ok" \
  --arg version "$version" \
  --argjson count "$count" \
  --argjson pages "$pages" \
  '{ok: $ok, version: $version, item_count: $count, pages: $pages}' \
  > "$outdir/report.json"
