# 243-ps1-csv-quoted

> "The invoice export has commas, escaped quotes, and one note that spans a line
> break. Turn it into totals without losing a record."

## Input

in/invoices.csv is RFC-style CSV with columns order_id, customer, note, units, and
unit_price. Fields may contain commas, doubled quotes, and embedded newlines. Empty
notes are valid.

## Rules

1. Parse the CSV structure; do not split physical lines or commas by hand.
2. Keep every order in input order.
3. Parse units as an integer and unit_price as an invariant decimal. Compute total as
   units multiplied by unit_price, rounded to two places away from zero.
4. Preserve the customer text in the output. The note is parsed but not reported.

## Output

Write exactly:

1. out/invoices.csv with header
   order_id,customer,units,unit_price,total
   and each numeric money field formatted with exactly two decimal places.
2. out/summary.json with exactly
   {"orders":4,"grand_total":12.80,"zero_quantity":1}.

## Messes to expect

- Acme, Inc. is one quoted field, not two columns
- doubled quotes are one literal quote
- the North Star note contains a physical newline inside a single CSV record
- zero quantity is a real order and contributes 0.00

## Timebox

Five minutes. Import-Csv already knows how to join quoted physical lines into records.
