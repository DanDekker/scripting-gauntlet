# 006-ragged-rows

> "This export is supposed to have four columns. It doesn't. Don't lose my rows."

## Task

`in/orders.csv` has a header row and six data rows. The header defines the shape:
**4 columns**. Some rows do not match it.

## Rules

1. **Too few fields** — pad the row with empty fields at the end until it has 4 columns.
   The row is kept.
2. **Too many fields** — keep the first 4 fields, discard the rest. The row is kept.
3. A field that is *present but empty* is not a shape problem. It stays empty.
4. Count the repairs: `padded` = rows that had too few fields, `truncated` = rows that
   had too many.

## Output

**`out/clean.csv`** — the header, then all six rows, every row exactly 4 columns.

**`out/summary.json`** — exactly three keys:

```json
{"rows": 6, "padded": 1, "truncated": 2}
```

`rows` counts data rows (not the header).

## Timebox

2 minutes. If you are writing a general-purpose CSV framework, stop — you need `NF` and
a loop.
