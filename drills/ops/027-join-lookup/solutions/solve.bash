#!/usr/bin/env bash
# 027-join-lookup — load the lookup in pass one, join in pass two.
set -euo pipefail

customers="${IN:?IN not set}/customers.csv"
orders="${IN:?IN not set}/orders.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
trap 'rm -f "$body"' EXIT

awk -F',' -v customers="$customers" -v outdir="$outdir" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
{
  if (trim($0) == "") next
  n = split($0, raw, ",")
  for (i = 1; i <= n; i++) F[i] = trim(raw[i])
  if (FILENAME == customers) {
    if (tolower(F[1]) == "customer_id") next
    key = tolower(F[1])
    name[key] = F[2]
    country[key] = F[3]
    next
  }
  if (tolower(F[1]) == "order_id") next
  cid = tolower(F[2])
  if (cid in name) { matched++; nm = name[cid]; cc = country[cid] }
  else { unmatched++; nm = "UNKNOWN"; cc = "??" }
  total += F[3] + 0
  orders++
  printf "%s,%s,%s,%s,%.2f\n", F[1], cid, nm, cc, F[3] + 0
}
END {
  summary = outdir "/summary.json"
  printf "{\"orders\":%d,\"matched\":%d,\"unmatched\":%d,\"total\":%.2f}\n", orders, matched, unmatched, total > summary
  close(summary)
}' "$customers" "$orders" | LC_ALL=C sort -t, -k1,1 > "$body"

{
  printf 'order_id,customer_id,name,country,amount\n'
  cat "$body"
} > "$outdir/enriched.csv"
