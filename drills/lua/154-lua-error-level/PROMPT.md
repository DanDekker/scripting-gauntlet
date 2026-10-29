# 154-lua-error-level

> "Half the lines in this config file are wrong and the parser dies on the first one.
> I want every bad line reported, with the reason, and the good lines kept."

## Input

`in/records.txt` — one directive per line:

```
alpha=1
beta=2
```

The file has blank lines, comment lines, and several kinds of bad directive.

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#`.
2. Every other line is a directive: a **key**, `=`, then a **value**. The key and the
   value are trimmed of surrounding whitespace. A key is nonempty and contains only
   letters, digits, `_` and `-`.
3. A directive is **accepted** when it has an `=`, its key is well formed, its value is a
   non-negative integer in decimal, and that key has not been accepted before.
4. When a directive is not accepted, record the failure and carry on with the next line.
   The **reason** is exactly one of these, with no extra text and no source location:
   | reason | when |
   | --- | --- |
   | `missing '='` | the line has no `=` |
   | `bad key` | the key is empty or has a character outside letters, digits, `_`, `-` |
   | `not an integer` | the value is not a non-negative integer in decimal |
   | `duplicate key` | the key was already accepted on an earlier line |
5. The reason string for a value failure quotes the offending value: the reason is
   `not an integer: three` for the value `three`, and `not an integer: 3.5` for `3.5`. The
   reason for a bad key quotes the offending key: `bad key: two words`. The reason for a
   duplicate quotes the key: `duplicate key: alpha`. `missing '='` has nothing after it.
6. The reason text must contain **no** `file:line:` prefix, no file name, and no
   position information of any kind. It is the text that was raised, unchanged.
7. A key that was rejected does not reserve the name: a later line with the same key is
   judged on its own merits.

## Output

Write exactly these files to `$OUT`:

1. **`out/errors.csv`** — header `line,reason`, then one row per failed directive, in
   file order. `line` is the 1-based number of the line in the file, counting every line
   including the blank and comment ones. The `reason` is written as plain text; a field
   containing a comma or a double quote is written in double quotes with any inner
   double quote doubled.
2. **`out/accepted.csv`** — header `key,value`, then one row per accepted directive, in
   file order.
3. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — how many lines the file has (int)
   - `accepted` — how many directives were accepted (int)
   - `errors` — how many directives failed (int)

   Print it as one compact JSON object: `{"lines":12,"accepted":6,"errors":5}`.

## Messes to expect

- `gamma=three` and `neg=-3` fail on the value; `three` and `-3` are quoted back
- `bad line` has no `=` at all
- `alpha=7` repeats a key that was already accepted, so it is a duplicate
- `two words=x` has a key with a space in it
- a rejected directive must not stop the ones after it

## Timebox

Four minutes. Raise the reason, catch it, and keep the reason text exactly as you raised
it.
