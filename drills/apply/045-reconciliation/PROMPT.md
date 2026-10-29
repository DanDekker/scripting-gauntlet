# 045-reconciliation

> "Finance wants the month-end recon. Our ledger says one thing, the bank feed says
> another, and I need the list of what does not line up before the close."

## Task

`in/ledger.csv` is our ledger (`ref,customer,amount`). `in/bank.csv` is the statement
(`ref,amount`). Match them on `ref` and classify every ref that appears in either file.

## Rules

1. Skip blank lines. The header line of each file is not data.
2. `ref` matches **case-insensitively**: trim it and uppercase it. Print it uppercased.
3. One ref may have several rows on one side — sum them. `ledger_total` and `bank_total`
   are the sums for that ref (0.00 when the ref is absent from that side).
4. Amounts are accounting money: trim, drop `$` and spaces, and a value wrapped in
   parentheses is **negative**: `(45.00)` is `-45.00`.
5. `delta` is `ledger_total - bank_total`, signed, two decimals.
6. `status` is decided in this order:
   - `missing_in_ledger` — no ledger rows for that ref;
   - `missing_in_bank` — no bank rows for that ref;
   - `amount_mismatch` — `abs(delta) > 0.005`;
   - `matched` — otherwise.

## Output

**`out/recon.csv`** — header `ref,ledger_total,bank_total,delta,status`, one row per ref,
sorted by `ref` **ascending**. Every money column has exactly two decimals.

**`out/summary.json`** — exactly these keys: `refs`, `matched`, `amount_mismatch`,
`missing_in_bank`, `missing_in_ledger` (integers), plus `ledger_total`, `bank_total`,
`delta` (numbers, two decimals).

## Messes to expect

- `$` in front of an amount, and one amount padded with spaces
- a parenthesised negative amount on the bank side
- lowercase refs on the bank side
- a ref duplicated in the ledger (it is a sum, and it will not match)
- a ref that exists on one side only, in each direction
- a blank line in one file

## Timebox

5 minutes. One awk pass over both files keyed by uppercased ref, then one sort.
