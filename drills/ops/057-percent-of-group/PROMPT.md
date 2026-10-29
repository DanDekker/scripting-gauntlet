# 057-percent-of-group

> "Which rep is carrying their region? Give me each row's slice of the region, and the
running slice as we walk down it."

## Task

`in/sales.csv` has `region,rep,amount` — one line per order.

## Rules

1. The group key is `region`, trimmed and **lowercased**.
2. `amount` is trimmed and read as money.
3. `pct` is `100 * amount / group_total`.
4. `cum_pct` is the running sum of the group's raw amounts, in the export order below,
   divided by the group total, times 100. It is **not** the sum of the rounded `pct`
   values — accumulate raw amounts and round once when printing.
5. Both percentages print with exactly two decimals (`printf "%.2f"`).
6. Blank lines are ignored and count as nothing.

## Output

**`out/shares.csv`** — header `region,rep,amount,pct,cum_pct`, sorted by `region`
**ascending**, then `amount` **descending**, then `rep` **ascending**. That sort order is
what `cum_pct` accumulates in.

**`out/summary.json`** — exactly three keys: `rows` (data rows), `groups`, `total` (sum of
all amounts, two decimals).

## Messes to expect

- `East`, `east` and ` east ` in the same region
- an amount padded with spaces
- three rows tied on amount in one group — the `rep` tie-break decides the running order
- a blank line

## Timebox

3 minutes. One pass for totals, one `sort`, one pass for the running share.
