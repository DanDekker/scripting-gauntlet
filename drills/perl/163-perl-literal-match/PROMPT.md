# 163-perl-literal-match

> "These search terms come from users. One of them has a parenthesis in it and the whole
> report died. Match the terms literally, please."

## Input

`in/queries.txt` — one query per line:

```
pattern|subject
a.b|za.by
```

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#`.
2. Split the line at the **first** `|`: everything before it is the **pattern**,
   everything after it is the **subject**. Both are trimmed. A line with no `|` is
   **invalid**.
3. The pattern is a **literal string**, not a regular expression: every character in it is
   itself. `a.b` must not match `aXb`, and `x*y` must not match `xxy`.
4. Report `found` (1 or 0), the 1-based `position` of the first occurrence (empty when
   there is none), and `count`, the number of **non-overlapping** occurrences. `aa`
   appears once in `aaa`.

## Output

Write exactly these files to `$OUT`:

1. **`out/matches.csv`** — header `pattern,found,position,count`, one row per query in
   input order. No field contains a comma, so plain comma separation is correct.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — queries parsed (int)
   - `matched` — queries whose pattern was found (int)
   - `invalid` — lines rejected for having no `|` (int)

   Print it as one compact JSON object: `{"lines":6,"matched":4,"invalid":0}`.

## Messes to expect

- `a.b` against `aXb`: a regex would match, a literal must not
- `x*y` against `xxy`: same trap, other metacharacter
- `a(b` would make a naive `/$pattern/` die with an unmatched-parenthesis error
- `aa` against `aaa` is **one** match, not two

## Timebox

Three minutes. `index` for the literal search, or `\Q...\E` if you insist on a regex.
