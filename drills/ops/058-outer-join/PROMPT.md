# 058-outer-join

> "We have quantities in one export and prices in another. I want every sku that appears in
*either* — and I want to see which side it came from."

## Task

`in/left.csv` is `sku,name,qty`. `in/right.csv` is `sku,price`. Join them on `sku`.

## Rules

1. The join key is `sku`, trimmed and **lowercased** on both sides; the output key is the
   lowercase form.
2. A key appears **at most once per file**. The fixture guarantees it; duplicates are out
   of scope, so do not invent a winner rule.
3. **Full outer join**: every key from either file comes out once. A missing side is empty
   text, never a dropped row and never `UNKNOWN`.
4. `qty` prints as an integer, `price` with exactly two decimals, `name` keeps its case.
5. `side` is `both`, `left` (left file only) or `right` (right file only).

## Output

**`out/joined.csv`** — header `sku,name,qty,price,side`, one row per key, sorted by `sku`
**ascending** (plain byte order, `LC_ALL=C`).

**`out/summary.json`** — exactly four keys: `keys` (rows in `joined.csv`), `both`,
`left_only`, `right_only`.

## Messes to expect

- a key padded with spaces on one side
- one sku only in the price file and one only in the inventory file
- a quantity of zero that must not be treated as missing
- a name that only exists on the left

## Timebox

3 minutes. Load one file, stream the other, then sweep the leftovers; sort at the end.
