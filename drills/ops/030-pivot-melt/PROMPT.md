# 030-pivot-melt

> "This quarter report is wide. Turn it into one row per region per quarter so I can load it."

## Task

`in/wide.csv` is one row per region, one column per quarter:

```
region,q1,q2,q3,q4
north,100.00,,50.00,
```

Melt it: wide to long.

## Rules

1. The **header defines the quarters** — read the column names from row 1, lowercase them, and
   emit one row per non-empty cell. Do not assume there are exactly four.
2. `region` is trimmed and lowercased. `quarter` is the lowercased header name.
3. A cell that is **empty after trimming** produces no row. A cell that is `0.00` is a real
   value and does produce a row.
4. `amount` is money with two decimals.

## Output

**`out/long.csv`** — header exactly `region,quarter,amount`, the melted rows, sorted by
`region` **ascending** then `quarter` **ascending**.

**`out/summary.json`** — exactly three keys: `regions`, `cells` (rows written), `total` (sum of
all emitted amounts).

## Messes to expect

- an empty cell in the middle of a row
- a padded cell (` 30.00 `)
- a genuine `0.00` that must not be dropped
- the same region in two cases

## Timebox

3 minutes. Header first, then one nested loop: region outer, value column inner.
