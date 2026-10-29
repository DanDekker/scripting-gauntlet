# 156-lua-sparse-array

> "This export has blank rows in the middle of it. The dashboard reads them as zeros, so I
> need to know which entries are actually missing and which are genuinely zero."

## Input

`in/values.txt` — one field per line. A line may be empty, and empty lines are real
positions in the data, not noise:

```
10
20

40
```

## Rules

1. Line **n** of the file is position **n**. An empty line is a **missing** entry: the
   position exists but carries no value. A line that holds a decimal integer is a
   **present** entry with that value.
2. A line that is neither empty nor a decimal integer is **invalid**: count it, and treat
   its position as missing.
3. A present entry whose value is `0` is a present entry. Zero is a value, not a gap.
4. Report the **positions**, not the values: the number of positions the file holds, how
   many carry a value, how many are missing, how many lines were invalid, the total of
   the present values, and the largest present value.

## Output

Write exactly these files to `$OUT`:

1. **`out/present.csv`** — header `position,value`, then one row per **present** entry,
   in file order. `position` is the 1-based line number. `value` is the integer.
2. **`out/summary.json`** — an object with exactly these keys:
   - `positions` — how many lines the file has (int)
   - `present` — how many positions carry a value (int)
   - `missing` — how many positions carry no value: an empty line and an invalid line
     both leave their position without a value (int)
   - `invalid` — how many lines were invalid (int)
   - `total` — the sum of the present values (int)
   - `max` — the largest present value, or 0 when there is none (int)

   Print it as one compact JSON object: `{"positions":8,"present":5,...}`.

## Messes to expect

- two lines in the middle are empty, so the table you build has holes in it
- one line holds `0`, which must be counted as present
- one line holds `twelve`, which is invalid: it counts as invalid **and** its position is
  missing
- positions 4 and 7 hold values even though position 3 is a hole, so a tool that stops at
  the first hole loses two of the entries

## Timebox

Four minutes. Do not use `#` or `ipairs` on a table you know has holes — count the
positions yourself.
