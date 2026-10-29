#!/usr/bin/env bash
# 047-orphan-check — collect parents, then check each child as its file arrives.
set -euo pipefail

indir="${IN:?IN not set}"
outdir="${OUT:?OUT not set}"
mkdir -p "$outdir"

customers="$indir/customers.csv"
orders="$indir/orders.csv"
items="$indir/items.csv"
tsv=$(mktemp)
trap 'rm -f "$tsv"' EXIT

awk -F',' -v customers="$customers" -v orders="$orders" -v items="$items" -v outdir="$outdir" -v tsv="$tsv" '
function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
function orphan(file, row, column, key, parent) {
  printf "%s\t%d\t%s\t%s\t%s\n", file, row, column, key, parent > tsv
  if (file == "orders.csv") orphan_orders++
  else orphan_items++
}
FNR == 1 { next }
{
  if (trim($0) == "") next
  if (FILENAME == customers) {
    customers_rows++
    parent_customer[trim($1)] = 1
    next
  }
  if (FILENAME == orders) {
    orders_rows++
    order_id = trim($1)
    customer_id = trim($2)
    parent_order[order_id] = 1
    if (customer_id != "0" && !(customer_id in parent_customer))
      orphan("orders.csv", orders_rows, "customer_id", customer_id, "customers.csv")
    next
  }
  if (FILENAME == items) {
    items_rows++
    order_ref = trim($2)
    if (!(order_ref in parent_order))
      orphan("items.csv", items_rows, "order_id", order_ref, "orders.csv")
  }
}
END {
  close(tsv)
  dst = outdir "/summary.json"
  printf "{\"customers\":%d,\"orders\":%d,\"items\":%d,\"orphan_orders\":%d,\"orphan_items\":%d,\"orphan_rows\":%d}\n",
    customers_rows, orders_rows, items_rows, orphan_orders + 0, orphan_items + 0,
    orphan_orders + orphan_items > dst
  close(dst)
}' "$customers" "$orders" "$items"

{
  printf 'child_file,child_row,column,key_value,parent_file\n'
  LC_ALL=C sort -k1,1 -k2,2n "$tsv" | tr '\t' ','
} > "$outdir/orphans.csv"
