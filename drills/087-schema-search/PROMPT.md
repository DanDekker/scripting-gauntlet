# 087-schema-search

> "Somewhere in this dump there is a table with a budget column and a sponsor column.
> Find the one with the most rows and tell me the total budget."

## Task

`in/hint.txt` names the columns: `columns: budget, sponsor`. `in/dump/` is a directory
tree of mixed files.

## Rules

1. Only `.csv` (comma) and `.tsv` (tab) files are considered; search recursively, without
   following symlinks.
2. The header is the first line. Strip a UTF-8 BOM and surrounding spaces and double
   quotes from each header cell, then compare case-insensitively.
3. A file matches when its header contains **every** wanted column.
4. `rows` counts non-blank lines after the header.
5. Among matches, the winner has the most rows; break ties by path ascending.
6. `total` is the sum of the winner's `budget` column, two decimals, located **by header
   name**, not by fixed position.
7. Order matches by path ascending.

## Output

- `out/matches.csv` - header `path,delimiter,columns,rows`; `delimiter` is `comma` or
  `tab`, `columns` is the header cell count. Paths relative to `in/dump/`.
- `out/found.json` - exactly three keys: `path`, `rows`, `total`.
- `out/summary.json` - exactly two integers: `files_scanned` (csv/tsv files opened),
  `matches`.

## Messes to expect

- a BOM and quoted header cells
- a tab-separated file with an extra column
- a table missing the sponsor column
- an empty file with a `.csv` name
- a correctly shaped table that is not a csv/tsv

## Timebox

4 minutes. Read the header first; only then count rows.
