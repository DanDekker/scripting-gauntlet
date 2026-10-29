# 162-perl-numify

> "Every one of these tokens is 'a number' to the loader. I want to know which are
> actually numbers, and what their integer part is."

## Input

`in/values.txt` — one token per line. Blank lines are ignored.

## Rules

1. Trim surrounding whitespace from the line; that trimmed text is the **token**.
2. A token is **valid** only when it matches this grammar exactly:
   `^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$` — an optional sign, then digits with an optional
   fractional part, or a leading point and digits. No exponent, no `0x` prefix, no
   thousands separator, no embedded spaces.
3. `kind` is `int` when the token has no `.`, and `decimal` when it does. A token that
   fails rule 2 has kind `invalid`.
4. `int_part` is the integer part of the token, **truncated toward zero** — `-3.7` gives
   `-3`, `-0.5` gives `0`, `.5` gives `0` — printed as a plain integer with no sign on
   zero and no leading zeros. An invalid token has an empty `int_part`.

## Output

Write exactly these files to `$OUT`:

1. **`out/values.csv`** — header `token,kind,int_part`, one row per non-blank line, in
   input order. The token is written as trimmed.
2. **`out/summary.json`** — an object with exactly these keys:
   - `rows` — non-blank lines (int)
   - `int` — tokens of kind `int` (int)
   - `decimal` — tokens of kind `decimal` (int)
   - `invalid` — tokens of kind `invalid` (int)

   Print it as one compact JSON object: `{"rows":10,"int":4,"decimal":4,"invalid":3}`.

## Messes to expect

- `0x10` is **invalid**: perl would numify it to 0 without complaining
- `1e3` is invalid: the grammar allows no exponent
- `abc` is invalid, and `"abc" == 0` being true in perl must not make it a number
- `010` is ten, not eight
- `-3.7` truncates toward zero to `-3`, and `-0.5` truncates to `0`

## Timebox

Three minutes. Validate with a pattern, then convert — not the other way round.
