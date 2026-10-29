# 023-filter-predicate

> "Give me the orders that actually count: paid, at least a hundred, in a region we ship to."

## Task

`in/orders.csv` has a header row and order rows, with some junk between them.

## Rules

1. Skip blank lines. **Trim whitespace** from every field before using it.
2. `amount` may carry a leading `$`. It is money — compare it as a number, print two decimals.
3. A row is **kept** only when all three hold:
   - `status`, lowercased, is `paid`;
   - `amount` is >= 100;
   - `region`, lowercased, is one of `west`, `east`, `north`.
4. Every other row is **dropped**. Dropped rows still count in `rows_in`.
5. In the output, `order_id`, `customer` are as given (trimmed); `region` and `status` are
   lowercased and trimmed.

## Output

**`out/kept.csv`** — header exactly `order_id,customer,region,status,amount`, then the
kept rows sorted by `amount` **descending**, ties by `order_id` **ascending**.

**`out/summary.json`** — exactly four keys: `rows_in` (data rows read, header excluded),
`kept`, `dropped`, `total` (sum of kept amounts, a number with two decimals).

## Messes to expect

- blank lines and space-padded fields
- `paid`, `PAID`, `Paid`, ` paid `
- a `$` in front of one amount
- an integer amount with no decimals
- a big order in a region we do not ship to (it is still dropped)

## Timebox

3 minutes. One `awk` pass: trim, lowercase, one `if`, accumulate. Sort at the end.
