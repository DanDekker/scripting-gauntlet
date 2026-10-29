# 040-extract-column

> "Can you just give me the list of hostnames from the server inventory?"

## Task

`in/servers.csv` has a header row, then one row per server.

## Rules

1. The column you want is the one named `host` in the header — do **not** assume it is the
   first column, read the header to find it. Match the header name case-sensitively after
   trimming.
2. A **data row** is any line after the header that is neither blank nor a comment. A
   comment line is one whose first non-space character is `#`.
3. Trim surrounding whitespace from the extracted value before printing it.
4. Keep the rows in **file order**. Do not sort, dedupe or filter on value.
5. `in/servers.csv` is well-formed: no quoted fields, no commas inside values.

## Output

**`out/hosts.txt`** — one host per line, file order, no header, no blank line at the end.

**`out/summary.json`** — exactly two keys:

- `rows` — how many data rows were written;
- `skipped` — how many lines were dropped because they were blank or a `#` comment
  (the header is neither, so it does not count here).

## Messes to expect

- padded fields (` web-02 `, ` 10.0.4.12 `)
- a blank line in the middle of the file
- a `# decommissioned` comment line
- CRLF line endings on one row

## Timebox

90 seconds. One awk pass: find the index on `NR == 1`, then print `$col`.
