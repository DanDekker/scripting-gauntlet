# 047-orphan-check

> "We're about to turn on foreign keys and the migration dies. Find me every child row
> whose parent doesn't exist."

## Task

`in/` has three related files: `customers.csv` (`customer_id,name`), `orders.csv`
(`order_id,customer_id,amount`) and `items.csv` (`item_id,order_id,sku,qty`).

Check two references: `orders.customer_id` against `customers.customer_id`, and
`items.order_id` against `orders.order_id`.

## Rules

1. Skip blank lines and each file's header. Keys are trimmed before comparing; compare
them case-sensitively.
2. Each reference is checked against **its own** parent file only. An order that is itself
   orphaned still satisfies any item that points at it.
3. `customer_id` of `0` means "guest checkout": it is allowed and is never an orphan.
4. `child_row` is the 1-based index of the row among that file's **non-blank data rows**
   (header excluded, blank lines not counted).
5. A child row is an orphan when its key has no matching parent row.

## Output

**`out/orphans.csv`** — header `child_file,child_row,column,key_value,parent_file`, one row
per orphan child row, sorted by `child_file` **ascending** then `child_row` **ascending**
(numeric). `child_file` and `parent_file` are base names, e.g. `orders.csv`.

**`out/summary.json`** — exactly six integers: `customers`, `orders`, `items` (data rows in
each file) and `orphan_orders`, `orphan_items`, `orphan_rows` (the two per-file counts and
their sum).

## Messes to expect

- a padded key (` 3 `) that must still match
- a guest order with `customer_id` `0`
- a blank line inside `orders.csv` that must not shift `child_row`
- an item pointing at a missing order, and an item pointing at an orphan order that exists

## Timebox

4 minutes. Load parents into a set as you go, check each child against it, sort at the end.
