# 161-perl-split-limits

> "These service records are colon-separated. Somebody left the score blank on the last
> field, and the loader silently dropped the whole record instead of the field."

## Input

`in/rows.txt` — one record per line, four colon-separated fields:

```
name:role:note:score
carol:admin:ok:10
bob:user:ok:
```

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#`.
2. Split the line on `:` into **exactly four** fields. An empty trailing field is a real
   field: `bob:user:ok:` has four fields, the last of them empty. A line that does not
   give exactly four fields is **invalid**.
3. `name` and `role` must be non-empty. `note` and `score` may be empty.
4. `score`, when it is not empty, must be a non-negative integer in decimal. Anything else
   is **invalid**.
5. Count `empty_notes` and `empty_scores` over the rows that were accepted, not over the
   rejected ones.

## Output

Write exactly these files to `$OUT`:

1. **`out/rows.csv`** — header `name,role,note,score`, one row per accepted record, sorted
   by `name` ascending in byte order. An empty note or score is an empty field.
2. **`out/summary.json`** — an object with exactly these keys:
   - `rows` — accepted records (int)
   - `empty_notes` — accepted records with an empty note (int)
   - `empty_scores` — accepted records with an empty score (int)
   - `invalid` — rejected lines (int)

   Print it as one compact JSON object: `{"rows":3,"empty_notes":1,...}`.

## Messes to expect

- `bob:user:ok:` ends in a colon: it is four fields with an empty score, not three fields
- `alice:admin::7` has an empty note in the middle
- `dave::x:3` has an empty role, which is invalid
- `eve:user:ok:5:extra` has five fields and `frank:user` has two: both invalid
- `:nobody:x:1` has an empty name: invalid

## Timebox

Three minutes. The limit argument is the whole drill: a split without `-1` throws the
empty trailing field away.
