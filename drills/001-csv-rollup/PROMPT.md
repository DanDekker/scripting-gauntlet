# 001-csv-rollup

> "The CRM export is a mess — can you tell me revenue by region for paid orders?
> It's got dupes and some junk rows in it. Should take you five minutes."

## Task

`in/orders.csv` is an export with one row per order *event*, not per order. Clean it and
roll it up. It is a UTF-8 CSV with the columns `order_id`, `customer`, `region`,
`status`, `amount`, and `updated_at`. The fixture is synthetic; no external
data or network access is needed.

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
Example,3,1234.50
```

Ordered by `revenue` **descending**, ties broken by `region` **ascending**. `revenue` is
formatted to exactly 2 decimal places. The example row illustrates the shape,
not an expected row from the fixture.

**`out/summary.json`** — one JSON object with exactly four keys:
`orders` (integer count of deduped paid orders with a parseable amount),
`regions` (integer count of regions in `regions.csv`), `revenue` (number rounded to
two decimals), and `dropped` (integer count of paid rows whose amount did not
parse). No extra keys.

## Messes to expect

- duplicate `order_id`s where the later row is the truth
- mixed-case region and status values
- trailing whitespace on some lines and at least one blank line
- a paid order with an empty amount
- amounts with a leading `$`

## Timebox

Aim for 4 minutes. Read only from `$IN`, write only under `$OUT`, and leave the
fixture untouched. Any language supplied for this drill may be used with its
standard tools; no package install is required. The output should be
deterministic. The harness's execution timeout is separate from this authoring
timebox.
