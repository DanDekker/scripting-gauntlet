#!/usr/bin/env bash
# 032-running-total — sort first, then accumulate per account.
set -euo pipefail

src="${IN:?IN not set}/ledger.csv"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

body=$(mktemp)
counts=$(mktemp)
trap 'rm -f "$body" "$counts"' EXIT

awk -F',' '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
NR == 1 { next }
{
  if (trim($0) == "") next
  printf "%s,%s,%s,%.2f\n", tolower(trim($3)), trim($2), trim($1), trim($4) + 0
}' "$src" | LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3n | awk -F',' -v counts="$counts" '
{
  if ($1 != acct) { acct = $1; accounts++; balance = 0 }
  balance += $4
  net += $4
  tx++
  printf "%s,%s,%s,%.2f\n", $1, $2, $4, balance
}
END {
  printf "%d %d %.2f\n", accounts, tx, net > counts
  close(counts)
}' > "$body"

read -r accounts tx net < "$counts"

{
  printf 'account,date,amount,balance\n'
  cat "$body"
} > "$outdir/running.csv"

printf '{"accounts":%d,"transactions":%d,"net":%s}\n' "$accounts" "$tx" "$net" \
  > "$outdir/summary.json"
