# 022-type-inference

> "The loader keeps guessing column types and quietly eating data. Show me where the guess
is wrong."

## Task

`in/columns.csv` is one page of a spreadsheet. Infer a type per column, and list every
value that a naive numeric cast would damage.

## Rules

**Type of a column** (consider every data cell, `row` included):

1. `integer` if every cell matches `^-?(0|[1-9][0-9]*)$` (no leading zeros, no sign but `-`).
2. otherwise `float` if every cell matches
   `^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?$` **and** at least one cell contains
   `.` or an exponent.
3. otherwise `string`.

**Offending value** — a single cell that the obvious cast would not round-trip. It is an
offender when any of these holds:

- it is integer text with a leading zero (`007`, `00000`): the cast drops the zeros;
- it is an integer whose magnitude exceeds `9007199254740991` (2^53 − 1): a double cannot
  hold it;
- it is `NaN` or `Infinity`, in any letter case and with an optional sign;
- it is a `0x`/`0X` hexadecimal literal;
- it matches no decimal shape above at all (`oops`).

Everything else is clean: `90210`, `-0.5`, `1e5` and `3.14` all survive a cast and are
not offenders.

## Output

**`out/types.csv`** — header `column,type`, one row per input column **in input order**.

**`out/offenders.csv`** — header `column,row,value`, one row per offending cell, sorted by
column in input order, then by `row` ascending (numeric). `row` is the value of the `row`
column for that line.

## Messes to expect

- a zip column that is all leading zeros except one
- an id column with a 16-digit value
- `1e5` sitting beside `0.5`
- `0x10`, `NaN` and `Infinity`
- a column of integers with one `oops` in it

## Timebox

3 minutes. Two regexes, one bookkeeping loop, and the offender rules as a checklist.
