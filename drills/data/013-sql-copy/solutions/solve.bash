#!/usr/bin/env bash
# 013-sql-copy — one flag: are we inside the block we want?
set -euo pipefail

src="${IN:?IN not set}/dump.sql"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

awk -v outdir="$outdir" '
BEGIN { orders = outdir "/orders.csv"; print "id,customer,region,amount" > orders }
/^COPY public\.orders / { inside = 1; next }
/^\\\.$/ { inside = 0; next }
inside {
  printf "%s,%s,%s,%s\n", $1, $2, $3, $4 > orders
  rows++
  total += $4
}
END {
  summary = outdir "/summary.json"
  printf "{\"rows\":%d,\"total\":%.2f}\n", rows, total > summary
  close(orders)
  close(summary)
}' "$src"
