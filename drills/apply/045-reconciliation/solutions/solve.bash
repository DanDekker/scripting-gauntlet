#!/usr/bin/env bash
# 045-reconciliation — uppercase the key, sum per side, classify by presence then delta.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

ledger="$indir/ledger.csv"
bank="$indir/bank.csv"
tsv=$(mktemp)
trap 'rm -f "$tsv"' EXIT

awk -F',' -v ledger="$ledger" -v outdir="$outdir" -v tsv="$tsv" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
function money(s,   sign) {
  s = trim(s)
  sign = 1
  if (s ~ /^\(.*\)$/) { sign = -1; gsub(/[()]/, "", s) }
  gsub(/[$ ]/, "", s)
  return sign * (s + 0)
}
FNR == 1 { next }
{
  if (trim($0) == "") next
  ref = toupper(trim($1))
  refs[ref] = 1
  if (FILENAME == ledger) { lsum[ref] += money($3); hasl[ref] = 1 }
  else                    { bsum[ref] += money($2); hasb[ref] = 1 }
}
END {
  for (ref in refs) {
    l = lsum[ref] + 0
    b = bsum[ref] + 0
    d = l - b
    if (!(ref in hasl))      status = "missing_in_ledger"
    else if (!(ref in hasb)) status = "missing_in_bank"
    else if ((d < 0 ? -d : d) > 0.005) status = "amount_mismatch"
    else                     status = "matched"
    count[status]++
    n++
    ltot += l
    btot += b
    printf "%s\t%.2f\t%.2f\t%.2f\t%s\n", ref, l, b, d, status > tsv
  }
  close(tsv)
  dst = outdir "/summary.json"
  fmt = "{\"refs\":%d,\"matched\":%d,\"amount_mismatch\":%d,\"missing_in_bank\":%d,\"missing_in_ledger\":%d,\"ledger_total\":%.2f,\"bank_total\":%.2f,\"delta\":%.2f}\n"
  printf fmt, n, count["matched"] + 0, count["amount_mismatch"] + 0,
    count["missing_in_bank"] + 0, count["missing_in_ledger"] + 0,
    ltot, btot, ltot - btot > dst
  close(dst)
}' "$ledger" "$bank"

{
  printf 'ref,ledger_total,bank_total,delta,status\n'
  LC_ALL=C sort -k1,1 "$tsv" | tr '\t' ','
} > "$outdir/recon.csv"
