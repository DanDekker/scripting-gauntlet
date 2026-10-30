# 228-perl-float-format

> "The invoice export came back with `3` where the ledger says `3.00`, with `2.67` where the
> spreadsheet says `2.68`, and the totals row was off by a cent. Three different number
> formats, three different answers."

## Input

`in/amounts.txt` — one amount per line, `<label> <amount>`:

```text
# name amount
alpha 2.675
bravo 0.125
charlie 1.005
delta 3.0
echo -2.5
foxtrot 3.5
golf 2.5
hotel +1.25
india .5
juliet 10.0
kilo 0.145
lima 4.5
mike -4.5
nina 0.1234567890123456789
oscar 3.9
peggy -3.9
```

Blank lines and lines whose first character is `#` are skipped. The label is the first
word; the amount is the rest of the line.

## Rules

1. Read `in/amounts.txt`, in file order. For each amount, parse it as a number and
   report three renderings of that number:
   - `plain` — the number as perl prints it in string context: **15 significant digits**,
     with no trailing `.0` on a whole number. So `3.0` is `3`, `10.0` is `10`, and
     `+1.25` is `1.25`.
   - `cents` — the number with **exactly two decimal places**. The value is the binary
     double rounded to the nearest, and an exact midpoint goes to the **even** digit:
     `0.125` is `0.12`.
   - `whole` — the number rounded to **zero decimal places**, again with a midpoint going
     to the **even** digit: `2.5` is `2`, `3.5` is `4`, `0.5` is `0`, `-2.5` is `-2`.
2. **`out/amounts.csv`** — header `label,plain,cents,whole`. One row per amount, in file
   order.
3. **`out/summary.json`** — keys `amounts`, `total_cents`, `max_plain`. One compact JSON
   object.
   - `amounts` — the number of amounts.
   - `total_cents` — the sum of all the amounts, rendered with exactly two decimal
     places, as a **string** (for example `"22.32"`).
   - `max_plain` — the largest amount, rendered like `plain`, as a **string**.

## Messes to expect

- Perl's default number printing is **not** a fixed-decimal format: it keeps 15
  significant digits and drops a whole number's `.0`. `3.0` prints `3`, and
  `0.1234567890123456789` prints `0.123456789012346`.
- `%.2f` formats the double, not the decimal text. `2.675` is really
  `2.67499999...`, so it prints `2.67` where rounding the decimal first gives `2.68`.
  `1.005` is really `1.00499999...` and prints `1.00`; `0.145` prints `0.14`.
  `0.125` is exact, so it is a midpoint and goes to the even digit: `0.12`.
- `%.0f` rounds a midpoint to even, not away from zero: `2.5` is `2` and `-2.5` is
  `-2`. A shell-free `round half up` gives `3` and `-3`.
- `int()` and `%d` **truncate** toward zero, so `3.9` becomes `3` where rounding gives
  `4`. They are not a rounding function.

## Timebox

Four minutes. Format the number; do not round it first and format the rounded value.
