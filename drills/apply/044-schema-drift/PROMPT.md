# 044-schema-drift

> "The nightly export keeps changing shape and nobody told us. Diff the headers of last
> week's four files and tell me what moved, what vanished, and where the types changed."

## Task

`in/daily/` holds four consecutive exports: `2026-09-28.csv`, `2026-09-29.csv`,
`2026-09-30.csv`, `2026-10-01.csv`. Each has a header and data rows. Compare their schemas.

## Rules

1. Column names are the header fields, **trimmed**. A leading UTF-8 BOM belongs to the
   file, not to the first column name — strip it. A column is "present" in a file when its
   trimmed name appears in that file's header, whatever its position.
2. Data rows are the non-blank lines after the header.
3. Per column, in **file-name order**: `first_seen` and `last_seen` are the file names where
   it first and last appears, `files_present` counts the files that have it.
4. `status`: `transient` if the column is missing from both the first and the last file;
   else `added` if it is missing from the first file; else `dropped` if it is missing from
   the last file; else `stable`.
5. Column **type** in a file, over that column's trimmed values in that file:
   - `absent` — the column is not in the file's header;
   - `empty` — present, but every value is empty;
   - `int` — every non-empty value matches `^-?[0-9]+$`;
   - `float` — not `int`, but every non-empty value matches `^-?[0-9]+(\.[0-9]+)?$`;
   - `text` — anything else.
6. A column **drifts** when its non-`empty`, non-`absent` types are not all the same.

## Output

**`out/columns.csv`** — header `column,first_seen,last_seen,files_present,status`, rows
sorted by `first_seen` **ascending**, then `column` **ascending**.

**`out/types.csv`** — header `column,2026-09-28,2026-09-29,2026-09-30,2026-10-01,drift`
(date columns exactly those four names, in that order), rows sorted by `column` ascending;
`drift` is `yes` or `no`.

**`out/files.csv`** — header `file,rows,columns`: one row per file, sorted by `file`
ascending; `rows` is data rows, `columns` is that file's header width.

**`out/summary.json`** — exactly these keys, all integers except none: `files`, `columns`
(distinct names across all files), `rows` (data rows across all files), `stable`, `added`,
`dropped`, `transient`, `type_drift` (how many columns drift).

## Messes to expect

- a BOM on one file's header
- a padded header name (` customer `)
- a column that exists for exactly one day (both `added` and `dropped`)
- a rename: `amount` disappears the same day `amount_usd` appears
- an amount column that is decimal on three days and whole numbers on one

## Timebox

5 minutes. One pass per file to collect presence and per-column type state, then two sorts.
