#!/usr/bin/env bash
# 028-anti-join — collect the active ids, then print everyone not in the set.
set -euo pipefail

customers="${IN:?IN not set}/customers.csv"
orders="${IN:?IN not set}/orders.csv"
outdir="${OUT:?OUT not set}"
cutoff="2026-02-01"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F',' -v customers="$customers" -v cutoff="$cutoff" -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
{
  if (trim($0) == "") next
  n = split($0, raw, ",")
  for (i = 1; i <= n; i++) F[i] = trim(raw[i])
  if (FILENAME == customers) {
    if (tolower(F[1]) == "customer_id") next
    key = tolower(F[1])
    if (!(key in known)) {
      known[key] = 1
      total++
      K[total] = key
      N[total] = F[2]
    }
    next
  }
  if (tolower(F[1]) == "order_id") next
  key = tolower(F[2])
  if (F[3] >= cutoff && (key in known)) active[key] = 1
}
END {
  quiet = 0
  for (i = 1; i <= total; i++) {
    if (K[i] in active) continue
    quiet++
    print K[i] "," N[i]
  }
  summary = outdir "/summary.json"
  printf "{\"customers\":%d,\"active\":%d,\"inactive\":%d}\n", total, total - quiet, quiet > summary
  close(summary)
}' "$customers" "$orders" | LC_ALL=C sort -t, -k1,1 > "$body"

{
  printf 'customer_id,name\n'
  cat "$body"
} > "$outdir/inactive.csv"
