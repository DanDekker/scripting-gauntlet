# 018-null-semantics

> "The export marks missing values every possible way. Clean that up."

## Task

`in/people.csv` has an `email` and an `age` column that were filled in by five different
systems, each with its own idea of "no value".

## Rules

1. These tokens mean **missing**: an empty field, `NA`, `N/A`, `null`, and `-`.
   Matching is **case-insensitive** (`n/a` and `N/A` are the same).
2. Missing values become **empty fields** in the output. Do not drop the row.
3. `0` is **not** missing. It is a value and must survive.
4. Count every field you converted.

## Output

**`out/clean.csv`** — the header, then all five rows, with missing values emptied:

```
id,name,email,age
2,Bob,,
```

**`out/summary.json`** — exactly two keys: `rows` and `nulls` (fields converted).

## Messes to expect

- the same missing value spelled five different ways
- a genuine `0` sitting in the same column as the missing values

## Timebox

2 minutes. One token list, one case fold, one counter.
