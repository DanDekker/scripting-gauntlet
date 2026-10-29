#!/usr/bin/env bash
set -euo pipefail

endpoints="${IN:?IN not set}/endpoints.txt"
out="${OUT:?OUT not set}"
work="${WORK:?WORK not set}"
base="${API_BASE:?API_BASE not set}"
[[ -f "$endpoints" ]] || { echo "missing endpoints: $endpoints" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }
printf 'endpoint,status,attempts,http_code,items\n' > "$out/results.csv"

total=0
ok=0
failed=0
requests=0
while IFS= read -r name || [[ -n "$name" ]]; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  [[ "$name" =~ ^[a-z]+$ ]] || { echo "bad endpoint: $name" >&2; exit 1; }
  total=$((total + 1))
  status=failed
  items=
  for attempt in 1 2 3; do
    code=$(curl --silent --show-error --connect-timeout 2 --max-time 5 \
      --output "$work/body.json" --write-out '%{http_code}' "$base/$name") \
      || { echo "transport failure: $name" >&2; exit 1; }
    requests=$((requests + 1))
    if [[ "$code" == 200 ]]; then
      items=$(jq -er '.items | if type == "array" then length else error("items is not an array") end' \
        "$work/body.json") || { echo "bad JSON: $name" >&2; exit 1; }
      status=ok
      break
    fi
    [[ "$code" == 503 ]] || break
  done
  if [[ "$status" == ok ]]; then ok=$((ok + 1)); else failed=$((failed + 1)); fi
  printf '%s,%s,%d,%s,%s\n' "$name" "$status" "$attempt" "$code" "$items" \
    >> "$out/results.csv"
done < "$endpoints"

printf '{"endpoints":%d,"ok":%d,"failed":%d,"requests":%d}\n' \
  "$total" "$ok" "$failed" "$requests" > "$out/summary.json"
