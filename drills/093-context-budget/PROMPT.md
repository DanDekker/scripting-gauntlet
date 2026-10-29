# 093-context-budget

> "I have a token budget for the agent's context and a pile of source files with priorities.
> Which files actually go in — and how much of the budget is left?"

## Input

- `in/files.csv` — header `path,tokens,priority`.
- `in/budget.txt` — a single integer: the token budget for this run.

The CSV is messy: blank lines, cells padded with spaces, a `path` that appears twice with
different token counts, a row with an empty `path`, a non-numeric token count, and a file
that costs zero tokens.

## Rules

1. **Clean the table.** Ignore any row with fewer than three fields, any row with an empty
   `path` (after trimming), and the header row. Trim every cell.
   A `tokens` value must be a non-negative integer — digits only after trimming (so `0` is
   valid and `tbd` is not). A `priority` value must be an integer, optionally negative.
   A row failing either check is ignored entirely.
2. **De-duplicate by `path`, last occurrence wins.** If a path appears more than once, keep
   the `tokens` and `priority` from its **last** valid row. A file with `tokens` = 0 is
   still a file and is still a candidate.
3. **Order the candidates** by `priority` ascending (1 = most important), then by `path`
   ascending in byte order (case-sensitive, `LC_ALL=C`). That pair is unique, so the order
   is fully determined.
4. **Greedy fill.** Walk that order once, keeping a `remaining` counter that starts at the
   budget. Include a file when `tokens <= remaining` and subtract its tokens from
   `remaining`; otherwise **skip that file and continue** to the next candidate. Never go
   back to a skipped candidate.

Every candidate that is not included — whether it did not fit or came after the budget ran
out — counts as skipped.

## Output

Write exactly these files to `$OUT`:

1. **`out/context.txt`** — the included paths, one per line, in inclusion order, with a
   trailing newline after the last one.
2. **`out/summary.json`** — an object with exactly these keys:
   - `budget` — the budget read from `in/budget.txt` (int)
   - `included` — number of included files (int)
   - `included_tokens` — sum of the tokens of the included files (int)
   - `skipped` — number of candidates that were not included (int)
   - `remaining` — budget left over, `budget - included_tokens` (int)

## Messes to expect

- the duplicate `path` row rewrites the earlier one — the first row's token count is a
trap
- ` 300 ` must parse as `300`; the padded cell is not a string
- the zero-token file must be included (it fits) and must not be silently dropped
- the file that does not fit must be skipped, and the walk must keep going: files later in
  the order can still be included

## Timebox

A few minutes. If you are past that, the approach is wrong.
