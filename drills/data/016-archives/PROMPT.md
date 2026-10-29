# 016-archives

> "One export is gzipped, one is a tarball. Same columns. Give me totals by region."

## Task

`in/` holds two compressed files, both containing CSV with the header
`id,region,amount`:

- `sales.csv.gz` — a gzip-compressed CSV
- `archive.tar.gz` — a tarball containing CSV members (one of them is at
  `oct/2026-10.csv`)

Both are real data. Read them and roll them up **together**.

## Rules

1. Decompress **to stdout** and pipe onward. Do not litter the working directory with
   extracted copies.
2. The tarball may contain members you do not want. Take the `.csv` members.
3. `amount` is a number.
4. Group by `region`.

## Output

**`out/by_region.csv`** — header, then one row per region:

```
region,amount,rows
South,250.00,2
```

Ordered by `amount` **descending**, ties by `region` ascending.

**`out/summary.json`** — exactly two keys: `files` (how many sources were read) and
`rows` (how many data rows in total).

## Messes to expect

- a tar member in a subdirectory, so the name is `oct/2026-10.csv`, not `2026-10.csv`
- a tarball containing a file that is not a CSV

## Timebox

4 minutes. `gzip -dc` and `tar -xzOf` are the whole toolkit.
