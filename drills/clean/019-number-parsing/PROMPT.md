# 019-number-parsing

> "Finance sent me a column of amounts typed by humans. I need the numbers, and I need
to know how many I could not read."

## Task

`in/amounts.csv` is a **semicolon-delimited** export (the European-Excel default) with two
columns: `id` and `raw`.

## Rules

1. Parse every `raw` value with exactly this pipeline, in this order:
   1. trim surrounding whitespace;
   2. if the whole value is wrapped in parentheses `(...)`, drop them and mark it **negative**;
   3. drop a leading currency symbol (`$`, `€` or `£`);
   4. remove every `,` (thousands separator);
   5. drop a trailing `%`. A percent sign is **display formatting only** — the number keeps
      its written value, so `12.5%` becomes `12.5`, **not** `0.125`;
   6. what is left must be a plain decimal number, optionally signed and optionally in
      scientific notation (`+7`, `-0.5`, and `1.5e3` which is `1500`).
2. Anything that does not survive the pipeline is **unparseable**: it contributes nothing to
   the total, gets an empty `value` cell, and is counted in `failed`.
3. `id` is copied through unchanged; row order is the input order, header row excluded.
4. Parsed values print with exactly two decimals.

## Output

**`out/parsed.csv`** — header `id,value`, one row per input row in input order; an
unparseable row has an empty `value`.

**`out/summary.json`** — exactly four keys: `rows` (data rows read), `parsed`, `failed`,
`total` (sum of the parsed values, two decimals).

## Messes to expect

- `$1,234.50` and `€250.00`
- `(89.99)`, which means minus
- `12.5%` and a padded `  +0.25%`
- `1.5e3`
- `n/a` and `abc`, which are not numbers at all

## Timebox

3 minutes. Strip the decoration, then let the machine convert one string.
