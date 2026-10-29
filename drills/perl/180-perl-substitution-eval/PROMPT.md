# 180-perl-substitution-eval

> "Every `key=value` on the line has to become `KEY:VALUE`, and the counter has to say how
> many were rewritten. The first version uppercased the wrong thing on some lines."

## Input

`in/assignments.txt` — one line of `key=value` pairs, separated by spaces:

```
a=1 b=2 c=3
x=10
```

Blank lines and `#` comments are skipped.

## Rules

1. Rewrite every `key=value` occurrence in place to `KEY:VALUE`: key and value both
   uppercased, the `=` replaced by `:`.
2. A value may be empty (`empty=` becomes `EMPTY:`), and keys are word characters.
3. Count the substitutions per line.
4. The rewrite must not depend on a nested match: if your replacement code matches the
   value again, the captures it uses afterwards are the **inner** ones.

## Output

Write exactly these files to `$OUT`:

1. **`out/rewritten.csv`** — header `line,text,substitutions`, one row per input line in
   order. The text contains no commas.
2. **`out/summary.json`** — keys `lines` and `substitutions`. One compact JSON object:
   `{"lines":4,"substitutions":7}`.

## Messes to expect

- `a=1 b=2 c=3` has three pairs on one line
- `empty=` has an empty value and still counts as a substitution
- `name=alice role=admin` uppercases both halves
- a nested `m//` inside the replacement block resets `$1`/`$2` — that is the bug to avoid

## Timebox

Five minutes. `s{(\w+)=(\S*)}{...}ge`, and copy `$1`/`$2` into lexicals at the top of the
block if you match anything else.
