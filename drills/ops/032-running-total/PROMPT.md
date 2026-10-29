# 032-running-total

> "Walk the ledger per account and show me the balance after every transaction."

## Task

`in/ledger.csv` has `id,date,account,amount` rows — one row per transaction, out of order.

## Rules

1. Sort by `account` **ascending**, then `date` **ascending**, then `id` **numeric ascending**.
   That third key is the tie-break for two transactions on the same day, and it is part of the
   contract.
2. `balance` is the running sum of `amount` **within the account**. It starts at zero at the
   first row of each account.
3. `account` is trimmed and lowercased; `amount` is money and may be negative.
4. Do not drop or merge rows — every transaction is one output row.

## Output

**`out/running.csv`** — header exactly `account,date,amount,balance`, all rows in the sort
order from rule 1.

**`out/summary.json`** — exactly three keys: `accounts`, `transactions`, `net` (sum of every
amount, which is also the sum of the final balances).

## Messes to expect

- rows in random order in the file
- two transactions on the same day for one account, ids 1 and 2
- a negative amount
- entries that net a second account to exactly zero

## Timebox

3 minutes. Sort, then one accumulator that resets when the account changes.
