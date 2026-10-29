#!/usr/bin/env bash
# 009-jsonl-stream — fold the stream with jq, never slurp it.
set -euo pipefail

src="${IN:?IN not set}/events.jsonl"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

fold=$(jq -n '
  reduce inputs as $e (
    {by_country: {}, tags: {}, events: 0, users: {}};
    .events += 1
    | .users[$e.user.id] = 1
    | .by_country[$e.user.country].events += 1
    | .by_country[$e.user.country].revenue += $e.amount
    | reduce $e.tags[] as $t (. ; .tags[$t] = ((.tags[$t] // 0) + 1))
  )
' < "$src")

{
  printf 'country,events,revenue\n'
  printf '%s\n' "$fold" | jq -r '
    .by_country | to_entries
    | map({country: .key, events: .value.events, revenue: .value.revenue})
    | sort_by([(-.revenue), .country])
    | .[] | "\(.country),\(.events),\(.revenue)"
  '
} > "$outdir/by_country.csv"

{
  printf 'tag,count\n'
  printf '%s\n' "$fold" | jq -r '
    .tags | to_entries
    | map({tag: .key, count: .value})
    | sort_by([(-.count), .tag])
    | .[] | "\(.tag),\(.count)"
  '
} > "$outdir/tags.csv"

printf '%s\n' "$fold" | jq '{events: .events, users: (.users | length)}' > "$outdir/summary.json"
