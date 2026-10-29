# 012-markdown-table

> "Numbers are in the README table. Copy them into a CSV please."

## Task

`in/report.md` contains a markdown document with one pipe table, plus prose.

## Rules

1. A markdown table looks like this:

   ```
   | region | qty | revenue |
   |--------|-----|---------|
   | North | 10 | 1250.00 |
   ```

   The second line is the **separator** row — it is not data.
2. Take **only** the rows of that table. Prose before and after it is not data.
3. Trim each cell. Parse `qty` as an integer and `revenue` as a number.
4. Keep the rows in document order.

## Output

**`out/table.csv`** — header, then the table's data rows:

```
region,qty,revenue
North,10,1250.00
```

**`out/summary.json`** — exactly three keys: `rows`, `total_qty`, `total_revenue`.

## Messes to expect

- cells padded with different amounts of whitespace
- a separator row made of dashes and pipes
- a sentence after the table that contains pipes in it

## Timebox

2 minutes. `grep '^\|'` finds the table; one `awk` finishes the job.
