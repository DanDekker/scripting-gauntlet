# 181-perl-substr-index

> "These are semicolon-separated pairs. I need the first key, the last key, how many pairs
> there are, and where the second `=` sits — by offset, not by splitting the line."

## Input

`in/pairs.txt` — one line of `key=value` pairs separated by `;`:

```
a=1;b=2;c=3
x=9
```

Blank lines and `#` comments are skipped.

## Rules

For each line report:

1. `first` — the text before the first `=`
2. `last` — the key of the last pair: everything after the last `;`, up to its `=`
3. `pairs` — the number of `=` characters
4. `second_eq` — the **1-based** position of the second `=`, or empty when there is only
   one
5. `head` — the first 5 characters of the line, or the whole line when it is shorter

## Output

Write exactly these files to `$OUT`:

1. **`out/fields.csv`** — header `line,first,last,pairs,second_eq,head`, one row per input
   line. The text contains no commas.
2. **`out/summary.json`** — keys `lines` and `pairs` (the total number of `=` counted).
   One compact JSON object: `{"lines":4,"pairs":7}`.

## Messes to expect

- `z=` has a single pair and an empty value: `last` is still `z`
- `a=1;b=2;c=3` has its second `=` at 1-based position 6
- a line shorter than 5 characters must not warn: `substr` past the end is a bug smell
- `index` returns `-1` when there is no second `=`; do not print `0`

## Timebox

Four minutes. `index`, `rindex`, `substr` — and remember the positions are 0-based.
