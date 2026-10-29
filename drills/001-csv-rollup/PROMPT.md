# 001-csv-rollup

> "The CRM export is a mess — can you tell me revenue by region for paid orders?
> It's got dupes and some junk rows in it. Should take you five minutes."

## Task

`in/orders.csv` is an export with one row per order *event*, not per order. Clean it and
roll it up.

## Rules

1. **Dedupe by `order_id`**, keeping the row with the **latest `updated_at`**. Timestamps
   are ISO 8601 UTC (`2026-03-02T09:00:00Z`), so they sort lexicographically.
2. **Keep only paid orders.** The `status` column is inconsistently cased (`paid`, `PAID`).
   Anything that is not paid after dedupe — `pending`, `cancelled` — is out.
3. **Normalize `region`**: trim, then Title Case (so `NORTH`, `north`, `North` are all
   `North`, and `East ` with a trailing space is `East`).
4. **Amounts** may carry a `$` and thousands separators (`$1,200.00`). Strip them, parse
   as a number, and round to 2 decimals. A row whose amount is blank or unparseable is
   **dropped and counted** — do not treat it as zero.

## Output

Write exactly two files to `$OUT`.

**`out/regions.csv`** — header, then one row per region that has at least one paid order:

```
region,orders,revenue
North,2,1500.00
```

Ordered by `revenue` **descending**, ties broken by `region` **ascending**. `revenue` is
formatted to exactly 2 decimal places.

**`out/summary.json`** — totals across paid orders:

```json
{"orders": 7, "regions": 4, "revenue": 3675.75, "dropped": 1}
```

`orders` counts deduped paid orders that had a parseable amount. `dropped` counts rows
that were paid but whose amount did not parse. No keys beyond these four.

## Messes to expect

- duplicate `order_id`s where the later row is the truth
- mixed-case region and status values
- trailing whitespace on some lines and at least one blank line
- a paid order with an empty amount
- amounts with a leading `$`

## Timebox

4 minutes. The version that takes 4 minutes is `awk` with a hash, or a 30-line python
script — not a pandas notebook and not a class.
