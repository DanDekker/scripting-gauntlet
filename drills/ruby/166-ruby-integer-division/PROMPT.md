# 166-ruby-integer-division

> "The ledger is in whole cents. When a month's total doesn't divide evenly across the
> days, the fraction carries forward — it does not vanish, and it does not round."

## Input

`in/balances.csv` — header `account,delta`, then one row per posting. `delta` is an
integer number of cents and **may be negative**.

```
account,delta
alice,10
bob,-22
```

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#` (the header is
   not a posting).
2. Sum `delta` and count postings per account.
3. `avg_cents` is `sum` divided by `count` with **floor** division: the quotient is the
   largest integer less than or equal to the real quotient. So `-15 / 2` is `-8`, and
   `-7 / 2` is `-4`.
4. `carry` is the remainder left over: `sum - avg_cents * count`. It is always `>= 0` and
   less than `count`.
5. Sort rows by `account` ascending in byte order.

## Output

Write exactly these files to `$OUT`:

1. **`out/averages.csv`** — header `account,sum,count,avg_cents,carry`, one row per
   account that has at least one posting.
2. **`out/summary.json`** — an object with exactly these keys:
   - `accounts` — distinct accounts (int)
   - `total` — sum of every delta (int)
   - `negative_accounts` — accounts whose `sum` is below zero (int)

   Print it as one compact JSON object: `{"accounts":5,"total":7,"negative_accounts":2}`.

## Messes to expect

- `bob` sums to `-15` over 2 postings: the floored quotient is `-8`, with `carry` 1
- `dana` sums to `-7` over 2 postings: `-4` with `carry` 1 — truncation would say `-3`
- `erin` sums to `5` over 3 postings: `1` with `carry` 2
- an account with a single posting has `carry` 0 and an average equal to that posting

## Timebox

Three minutes. In Ruby, `/` and `%` on Integers already floor — the bug is reaching for a
float and `to_i` first.
