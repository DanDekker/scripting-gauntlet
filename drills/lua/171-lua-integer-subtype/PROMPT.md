# 171-lua-integer-subtype

> "Two of these numbers are integers and two are floats, and the report has to say which.
> Then the counter wrapped and nobody noticed."

## Input

- `in/values.txt` — one token per line
- `in/counters.txt` — one integer token per line, to be summed with wrapping

Blank lines and lines starting with `#` are skipped.

## Rules

1. Parse a token with `tonumber`, which accepts decimal, a leading sign, and `0x` hex.
   A token that does not parse is **invalid**.
2. `kind` is the value's number subtype: `integer` or `float`. `0x10` is an integer.
3. For every valid token report:
   - `quotient` — the value `// 7` (floor division), printed with `tostring`
   - `remainder` — the value `% 7` (floor modulo), printed with `tostring`
   - `fmod` — `math.fmod(value, 7)`, printed with `tostring`
4. `//` and `%` keep the subtype: an integer operand pair gives an integer result, a float
   operand pair gives a float result. `tostring` prints floats with their `.0`.
5. Sum the integer values in `counters.txt` with **wrapping** 64-bit arithmetic: an
   overflow past `math.maxinteger` continues at `math.mininteger`.

## Output

Write exactly these files to `$OUT`:

1. **`out/values.csv`** — header `token,kind,quotient,remainder,fmod`, one row per non-blank
   token, in input order. The token is echoed as written. An invalid token has empty
   `quotient`, `remainder` and `fmod`.
2. **`out/counters.csv`** — header `total,total_hex,wrapped`, exactly one row. `total` is
   the wrapped sum, `total_hex` is that sum as 16 lowercase hex digits
   (`string.format("%x", total)`), and `wrapped` is `true` when the sum overflowed.
3. **`out/summary.json`** — an object with exactly these keys: `rows` (non-blank tokens),
   `integers`, `floats`, `invalid`. One compact JSON object:
   `{"rows":10,"integers":7,"floats":2,"invalid":1}`.

## Messes to expect

- `-10 // 7` is `-2` and `-10 % 7` is `4`, but `math.fmod(-10, 7)` is `-3`: two different
  remainder rules in the same report
- `-0.5 // 7` is `-1.0` and `-0.5 % 7` is `6.5`: floats floor too, and print with `.0`
- `0x10` is an integer 16; `-0x10` is an integer -16
- `math.maxinteger + 1` wraps to `math.mininteger`, whose hex is `8000000000000000`
- `abc` is invalid

## Timebox

Five minutes. `//` and `%` already floor — `math.fmod` does not, and mixing them is the
bug this drill is about.
