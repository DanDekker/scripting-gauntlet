# 235-perl-csv-parser

> "Our order ingestion script choked on customer names like `\"Smith, John\"` and notes
> containing `\"\"quoted\"\"` text. It did a naive `split /,/`, tearing addresses and notes
> into phantom columns and dropping orders."

## Input

`in/orders.csv` — CSV file adhering to RFC 4180:
- Header: `order_id,customer,product,amount,notes`
- Fields containing commas or quotes are wrapped in double quotes (`"..."`).
- Double quotes within quoted fields are escaped as `""`.
- Some rows may be malformed (differing column count).

```csv
order_id,customer,product,amount,notes
101,Acme Corp,"Widget, Deluxe",199.99,"rush order"
102,"Smith, John","Standard Bolt",4.50,"pickup at ""Warehouse A"""
103,Beta LLC,Anchor,45.00,
104,"Doe, Jane","Cable, 10ft",25.50,"handle with care"
105,Corrupt,Row,Missing,Fields,Extra
106,"O'Reilly, Tim","Manual, ""Perl Tips""",50.00,"gift wrapped"
```

## Rules

1. Parse each line of `in/orders.csv`, handling RFC 4180 quoted fields:
   - Fields may be unquoted or enclosed in `"..."`.
   - Embedded commas within quotes do not delimit fields.
   - Escaped double quotes (`""`) must be unescaped to single double-quotes (`"`).
   - Stripped enclosing quotes are removed from the parsed field values.
2. Validate field counts against the header (5 fields):
   - If a row does not have exactly 5 fields, mark it as `malformed` and do not include
     it in the output TSV.
3. **`out/clean.tsv`** — tab-separated values (`\t`) for valid rows:
   - Header: `order_id\tcustomer\tproduct\tamount\tnotes`
   - In input order.
4. **`out/summary.json`** — keys `total_rows`, `valid`, `malformed`, `total_amount`.
   - `total_rows` — data rows inspected (excluding header).
   - `valid` — number of rows written to `out/clean.tsv`.
   - `malformed` — number of malformed rows dropped.
   - `total_amount` — sum of `amount` across valid rows, rounded to 2 decimal places.
   - Emit as a single compact JSON object.

## Messes to expect

- Commas inside quoted strings: `"Widget, Deluxe"` is a single column value.
- Doubled quotes: `""Warehouse A""` inside quotes must become `"Warehouse A"`.
- Empty trailing fields: row 103 has an empty `notes` field.

## Timebox

Five minutes.
