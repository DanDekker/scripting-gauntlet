# 028-anti-join

> "Which customers went quiet? Anyone with no order since February 1st goes on the list."

## Task

`in/customers.csv` (`customer_id,name,signup`) is everyone. `in/orders.csv`
(`order_id,customer_id,order_date,amount`) is what they bought.

## Rules

1. Keys are trimmed and **lowercased** on both sides.
2. An order counts for this period when its `order_date` is **on or after** `2026-02-01`
   (ISO dates compare correctly as text).
3. A customer is **active** if at least one of their orders counts. Output only customers
   with **no** such order.
4. An order whose `customer_id` is not in `customers.csv` is ignored — it cannot make a
   customer quiet.

## Output

**`out/inactive.csv`** — header exactly `customer_id,name`, the quiet customers, sorted by
`customer_id` **ascending**. `name` as given (trimmed).

**`out/summary.json`** — exactly three keys: `customers` (rows in the customer file),
`active`, `inactive`.

## Messes to expect

- a lowercased id in one file, uppercase in the other
- an id padded with spaces
- two orders from the same customer, only one of them recent
- an order for a customer that does not exist
- an order dated before the cutoff

## Timebox

3 minutes. `awk` over both files: collect active ids, then print everyone who is not in it.
