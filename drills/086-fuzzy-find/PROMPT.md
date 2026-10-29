# 086-fuzzy-find

> "I need the budget spreadsheet I made in March. I think it's a CSV, probably under
> Desktop or Downloads, and small. Find it and tell me what's in it."

## Task

`in/hint.txt` is what the human remembers, one `key: value` per line: `keywords`,
`extension`, `max_size`, `roots`. The tree is `in/tree/`, with the human's home at
`in/tree/home/pp/`.

## Rules

1. Ignore blank and `#` lines in the hint.
2. `roots` are directories under `home/pp/`; search each recursively, without following
   symlinks and without descending into dot-directories.
3. `scanned` counts every regular file found under those roots.
4. A file is a **candidate** when all three hold: its extension equals `extension`
   (case-insensitive), its size is `<= max_size`, and its **basename** contains at least
   two of the hint keywords (case-insensitive substring).
5. `score` is the number of distinct keywords found in the basename.
6. Order candidates by score descending, then modification time descending, then path
   ascending (`LC_ALL=C`).
7. The first candidate is the winner. Read it as CSV with header `month,amount`: `rows` is
   the number of data rows, `total` the sum of `amount`, two decimals.

## Output

- `out/candidates.csv` - header `path,score`, one row per candidate, in the order above.
  `path` is relative to `in/tree/`, e.g. `home/pp/Desktop/march-budget.csv`.
- `out/found.json` - exactly four keys: `path`, `score`, `rows`, `total`.
- `out/summary.json` - exactly two integers: `scanned`, `candidates`.

## Messes to expect

- a matching name whose extension is not `csv`
- a matching name that is too large
- a matching CSV outside the roots
- several candidates that all score 2, separated only by mtime
- an empty CSV with the right header

## Timebox

5 minutes. Two passes: filter and score, then read the winner.
