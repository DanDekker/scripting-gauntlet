# 027-join-lookup

> "Attach the customer name and country to every order. If the customer is gone, say so."

## Task

`in/orders.csv` is the fact table (`order_id,customer_id,amount`). `in/customers.csv` is the
lookup (`customer_id,name,country`). Join them.

## Rules

1. The join key is `customer_id`, trimmed and **lowercased** on both sides. Output the key
   lowercase.
2. When a `customer_id` appears twice in `customers.csv`, the **last** row wins.
3. **Left join**: every order comes out, matched or not. An unmatched order gets
   `name` = `UNKNOWN` and `country` = `??`. An empty `customer_id` is simply unmatched.
4. `amount` stays money with two decimals; `name` and `country` keep their case.

## Output

**`out/enriched.csv`** — header exactly `order_id,customer_id,name,country,amount`, sorted by
`order_id` **ascending**.

**`out/summary.json`** — exactly four keys: `orders`, `matched`, `unmatched`, `total`
(sum of all order amounts, matched or not).

## Messes to expect

- the same customer id in two cases (`C-02`, `c-02`)
- a padded id (` C-01 `)
- an order for a customer the table does not have
- an order with no customer id at all
- a duplicate `customer_id` in the lookup, later row different

## Timebox

3 minutes. `awk` with two files: `NR == FNR` loads the lookup, the second pass joins.
