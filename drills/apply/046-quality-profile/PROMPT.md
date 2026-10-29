# 046-quality-profile

> "Before we load this customer export into the warehouse, tell me how bad it is. Per
> column: nulls, distinct, range, most common value."

## Task

`in/customers.csv` is a header plus ten data rows, one per customer.

## Rules

1. Skip blank lines. `rows` is the number of data rows.
2. A cell is **null** when, after trimming it, it is empty or equals — case-insensitively —
   one of `null`, `n/a`, `na`, `none`, `-`. Everything else is a non-null value, trimmed.
3. All counts are per column over those `rows` data rows.
4. `distinct` counts distinct trimmed non-null values, compared **case-sensitively**.
5. `numeric` is `yes` when a column has at least one non-null value and **every** non-null
   trimmed value matches `^-?[0-9]+(\.[0-9]+)?$`; otherwise `no`.
6. `min`/`max` are the numeric minimum and maximum printed with two decimals for a numeric
   column, and **empty** for every other column.
7. `top_value` is the most frequent trimmed non-null value; ties go to the value that
   occurs **first** in the file. `top_count` is its frequency, `0` if the column has no
   non-null value (and then `top_value` is empty too).

## Output

**`out/profile.csv`** — header exactly
`column,non_null,nulls,distinct,numeric,min,max,top_value,top_count`, one row per column,
sorted by `column` **ascending**.

**`out/summary.json`** — exactly five keys: `rows`, `columns`, `nulls` (total nulls across
all columns), `worst_column` (the column with the most nulls; ties broken by column name
ascending) and `worst_nulls`.

## Messes to expect

- an empty cell, a whitespace-only cell, `NULL` and `-` in the same file
- a padded email (`  cy@example.com `)
- a value repeated five times and a two-way tie at the top of another column
- a column with a missing date and a column that is all nulls except two rows

## Timebox

4 minutes. One awk pass, a counter per column, then one sort of the report rows.
