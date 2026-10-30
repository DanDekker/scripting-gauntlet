# 204-perl-map-scalar-context

> "The revenue report started saying the paid total was 3. That is the number of paid
> invoices, not the money. The old line was `my $total = map { $_->{amount} } @paid;`
> — and `map` in scalar context hands back a count."

## Input

`in/invoices.csv` — a header row `id,customer,amount,status`, then one invoice per line:

```csv
id,customer,amount,status
A1,acme,120.50,paid
A2,globex,80.00,paid
A3,initech,45.25,unpaid
A4,umbrella,310.75,paid
A5,soylent,12.00,unpaid
```

## Rules

1. Parse `in/invoices.csv`. The first line is the header; every later line is
   `id,customer,amount,status`.
2. An invoice is **paid** when `status` is exactly `paid`.
3. Report:
   - `invoices` — the number of invoices.
   - `paid_count` — the number of paid invoices.
   - `paid_total` — the sum of the amounts of the paid invoices.
   - `unpaid_count` — the number of invoices that are not paid.
   - `largest_paid_id` — the id of the paid invoice with the greatest amount. If two
     paid invoices tie on amount, the one that appears **first** in the file wins.
4. **`out/paid.csv`** — header `id,amount`. One row per paid invoice, in file order.
   `amount` is the text exactly as it appears in the file.
5. **`out/summary.json`** — keys `invoices`, `paid_count`, `paid_total`,
   `unpaid_count`, `largest_paid_id`. One compact JSON object.

## Messes to expect

- `map` in scalar context returns the **number of elements generated**, so
  `my $total = map { $_->{amount} } @paid;` yields the count, not the sum. Sum the
  list, or add in a loop.
- Amounts are text. `"310.75" > "120.50"` is a string comparison, and adding a string
  to a number numifies it.

## Timebox

Four minutes.
