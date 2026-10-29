# 013-sql-copy

> "Grab the orders table out of the dump. It's huge, don't read the whole thing."

## Task

`in/dump.sql` is a PostgreSQL dump. It contains **two** `COPY` blocks. Extract only the
one for `public.orders`.

## Rules

1. A `COPY` block starts with a line like
   `COPY public.orders (id, customer, region, amount) FROM stdin;`
   and ends with a line containing exactly `\.`
2. Only the `public.orders` block is data. The `public.customers` block must not appear
   in your output.
3. Inside the block, fields are **tab-separated**. `amount` is a number.
4. The terminating `\.` is not a row.

## Output

**`out/orders.csv`** — header, then the block's rows in order:

```
id,customer,region,amount
1,ACME,North,1250.00
```

**`out/summary.json`** — exactly two keys: `rows` and `total` (the sum of `amount`).

## Messes to expect

- another `COPY` block for a different table
- `SET` statements and comments before the block
- a `\.` line that ends the *other* block

## Timebox

3 minutes. One `awk` with a flag: are we inside the block we want?
