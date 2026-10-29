# 024-dedupe-exact

> "Our signup export has the same people in it three times. One row each, keep the first."

## Task

`in/signups.csv` has a header and signup rows, with exact repeats and whitespace noise.

## Rules

1. Skip blank lines. Rows are counted in `rows_in` whether or not you keep them.
2. **Trim** every field first. Two rows are duplicates only if all four trimmed fields are
   byte-identical **after trimming**.
3. Comparison is case-**sensitive**: `pro` and `PRO` are different plans, so those rows are
   not duplicates.
4. Keep the **first** occurrence of each distinct row, in the order it first appeared in the
   file. Never sort this output.

## Output

**`out/deduped.csv`** — header exactly `email,name,plan,signed_up`, then the unique rows in
first-seen order.

**`out/summary.json`** — exactly three keys: `rows_in`, `unique`, `dropped`. No totals, no
per-plan counts — just the three integers.

## Messes to expect

- a row repeated verbatim three times
- the same row again with trailing spaces on the last field
- a blank line in the middle of the file
- the same person and date with a *different* plan casing

## Timebox

3 minutes. Trim into a key, keep a `seen` set, print only the first hit.
