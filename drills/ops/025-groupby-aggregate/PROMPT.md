# 025-groupby-aggregate

> "Finance wants revenue by region by month, and the average order with it."

## Task

`in/sales.csv` has `date,region,rep,amount` rows for one quarter.

## Rules

1. The **group key** is `region` (trimmed, lowercased) plus the month, which is the first 7
   characters of `date` (`2026-01-03` becomes `2026-01`).
2. `amount` is money, trimmed. A row whose `amount` is empty has nothing to aggregate:
   count it in `skipped` and leave it out of every group.
3. Blank lines are neither rows nor skipped rows — ignore them silently.
4. `avg_order` is `revenue / orders`, printed with two decimals.

## Output

**`out/rollup.csv`** — header exactly `region,month,orders,revenue,avg_order`, one row per
(region, month) group, sorted by `region` **ascending** then `month` **ascending**.

**`out/summary.json`** — exactly four keys: `rows_in` (data rows read, header and blank
lines excluded), `skipped`, `groups`, `revenue` (grand total of aggregated amounts).

## Messes to expect

- the same region spelled `west`, `West`, `WEST`, and ` west `
- an amount padded with spaces
- a row with a region but no amount

## Timebox

3 minutes. One `awk`: build the key, accumulate, print at the end, sort the output.
