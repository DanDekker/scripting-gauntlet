# 170-ruby-float-format

> "The CSV came back with `1.0e+20` in one cell and `3.0` in another, and the accountant's
> checker wants exactly two decimals everywhere."

## Input

`in/amounts.txt` — one token per line. Blank lines are skipped.

## Rules

1. Trim the line; that text is the **token**.
2. A token is valid only when it matches `^-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$`.
   Anything else is **invalid**.
3. `kind` is `int` when the token has neither a `.` nor an exponent, and `float` otherwise.
4. An `int` formats as plain decimal digits.
5. A `float` formats with **exactly two decimals**, rounded **half away from zero**, and
   **never** in scientific notation. So `1e20` is `100000000000000000000.00`, `3.0` is
   `3.00`, `2.675` is `2.68`, and `1.005` is `1.01`.

## Output

Write exactly these files to `$OUT`:

1. **`out/formatted.csv`** — header `raw,kind,formatted`, one row per non-blank line, in
   input order. An invalid token has an empty `formatted`.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — non-blank lines (int)
   - `int` — tokens of kind `int` (int)
   - `float` — tokens of kind `float` (int)
   - `invalid` — tokens of kind `invalid` (int)

   Print it as one compact JSON object: `{"lines":8,"int":2,"float":5,"invalid":1}`.

## Messes to expect

- `1e20` must print in full, not as `1.0e+20`
- `3.0` must print `3.00`, not `3.0`
- `1.005` is the trap: `format("%.2f", 1.005)` gives `1.00` because the double is slightly
  below 1.005, while `1.005.round(2)` gives `1.01`
- `2.675` is the same family and must give `2.68`
- `-0.5` must print `-0.50`
- `abc` is invalid: empty `formatted`

## Timebox

Three minutes. Round first (`round(2)`), then format; `to_s` is not a formatter.
