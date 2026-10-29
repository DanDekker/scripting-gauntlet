# 008-fixed-width

> "Old mainframe export. Fixed width, no delimiter, no header. Make it a CSV."

## Task

`in/inventory.dat` is a fixed-width report. There is **no header row** and **no
delimiter** — fields are cut at fixed character positions.

## Layout

Each record is exactly 27 characters, in this order:

| field | chars | position | alignment |
| --- | --- | --- | --- |
| `name` | 8 | 1–8 | left, padded with spaces |
| `dept` | 6 | 9–14 | left, padded with spaces |
| `qty` | 4 | 15–18 | right, padded with spaces |
| `price` | 9 | 19–27 | right, padded with spaces |

Rules:

1. **Trim** every field. A name of all spaces is an **empty name** — keep the row, do
   not skip it.
2. `qty` and `price` are integers/amounts: trim, then parse. `price` has two decimals.
3. `total` = `qty` × `price`, rounded to 2 decimals.
4. Preserve the original record order.

## Output

**`out/inventory.csv`** — header plus one row per record:

```
name,dept,qty,price,total
ALICE,SALES,12,125.50,1506.00
```

**`out/summary.json`** — exactly two keys: `records` (the count) and `blank_names` (rows
whose name trimmed to empty).

## Messes to expect

- a record whose name field is entirely spaces
- numbers that are right-aligned, so they arrive with leading spaces
- names that are shorter than their field, so the next field starts early

## Timebox

3 minutes. `substr` in awk, slices in python. Do not try to split on whitespace — the
name field can contain spaces.
