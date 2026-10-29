# 026-topn-per-group

> "Who are the top two reps in each region? And yes, I care which one wins a tie."

## Task

`in/sales.csv` has `region,rep,amount` rows.

## Rules

1. `region` is trimmed and lowercased; `rep` is trimmed and keeps its case.
2. Ties in `amount` are broken by `rep` **ascending** — that ordering decides who makes the
   cut, so a region whose third place ties with second keeps the alphabetically earlier rep.
3. `rank` is the position **within the region** after sorting: 1 or 2. It restarts at 1 for
   every region.
4. Regions with only one row still get one row out; there is no padding.

## Output

**`out/top2.csv`** — header exactly `region,rank,rep,revenue`, sorted by `region`
**ascending**, then `rank` **ascending**. Because rank encodes the sort, that is the same as
revenue descending, ties by rep ascending.

**`out/summary.json`** — exactly three keys: `regions`, `rows_in` (data rows read),
`rows_out` (rows written).

## Messes to expect

- `west`, `West`, and ` west ` in the same file
- a region where two reps tie exactly on revenue
- a region with a single row
- a region with four rows, so two are cut

## Timebox

3 minutes. One sort (region asc, revenue desc, rep asc), then a counter per region.
