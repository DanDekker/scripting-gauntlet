# 177-ps1-decimal-money

> "Finance wants two decimals and half-cents rounded up. The report has 1.00 where the
> invoice says 1.01, and one total came back with fifteen digits."

## Input

`in/amounts.csv` — header `account,amount`, one row per charge. `amount` is a decimal
written with up to three fractional digits.

```
account,amount
alice,10.10
carol,1.005
```

## Rules

1. Sum each account's amounts **exactly**, as decimal values — a double sum is not the
   same number.
2. Round the account total to two decimals, **half away from zero**: `1.005` becomes
   `1.01`, `2.675` becomes `2.68`, `-0.5` would become `-0.50`.
3. Format the total with exactly two decimals, no thousands separator.
4. `items` is the number of rows for that account.
5. Sort accounts ordinal (byte) ascending.

## Output

Write exactly these files to `$OUT`:

1. **`out/totals.csv`** — header `account,total,items`, one row per account.
2. **`out/summary.json`** — an object with exactly these keys:
   - `accounts` — rows in `totals.csv` (int)
   - `total` — the grand total after rounding, formatted with two decimals (string)
   - `half_cents` — accounts whose exact sum has a third decimal digit of 5 (int)

   One compact JSON object: `{"accounts":5,"total":"15.35","half_cents":3}`.

## Messes to expect

- `carol` has exactly `1.005`: half away from zero is `1.01`, banker's rounding gives `1.00`
- `dave` has exactly `2.675`: `2.68` away from zero; a `-f` format string prints `2.67`
- `eve` is `0.1 + 0.2`: a double sum is `0.30000000000000004`, a decimal sum is `0.30`
- `alice` has two rows and must total `10.15`
- `frank` has `1.005` and `0.000`: the zero changes nothing and the row count still is 2

## Timebox

Five minutes. `[decimal]`, then `[decimal]::Round($v, 2, 'AwayFromZero')`, then
`.ToString('F2')`. Never `Measure-Object -Sum` on money.
