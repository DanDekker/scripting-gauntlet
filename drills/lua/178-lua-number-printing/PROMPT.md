# 178-lua-number-printing

> "The report goes to a diff. Two runs of the same values must print the same way, and
> right now the floats and the integers don't look alike."

## Input

`in/numbers.txt` — one numeric token per line. Blank lines and `#` comments are skipped.

## Rules

1. Parse a token with `tonumber`. A token that does not parse is **invalid**.
2. For every valid token report three renderings:
   - `plain` — `tostring(value)`, Lua's own rendering
   - `full` — `string.format("%.17g", value)`, seventeen significant digits
   - `short` — `string.format("%.6g", value)`, six significant digits
3. `kind` is `math.type(value)`: `integer` or `float`.
4. `scientific` in the summary counts rows whose `plain` contains an `e`.

## Output

Write exactly these files to `$OUT`:

1. **`out/numbers.csv`** — header `token,kind,plain,full,short`, one row per token in input
   order. An invalid token has empty renderings.
2. **`out/summary.json`** — an object with exactly these keys: `rows`, `integers`,
   `floats`, `invalid`, `scientific`. One compact JSON object:
   `{"rows":10,"integers":3,"floats":6,"invalid":1,"scientific":2}`.

## Messes to expect

- `1.0` prints `1.0` with `tostring` but `1` with `%.17g`: the subtype shows
- `1e15` is a float and prints `1e+15`; `1000000000000000` is an integer and prints in full
- `9007199254740993` (2^53+1) prints exactly, while `%.17g` gives `9007199254740992`
- `0.1` prints `0.1` but `%.17g` exposes `0.10000000000000001`
- `abc` is invalid

## Timebox

Five minutes. Run the values through all three renderings and compare — do not assume
`tostring` is `%g`.
