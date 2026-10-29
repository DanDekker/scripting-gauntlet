# 150-lua-pattern-fields

> "This report card is one `key=value` per line, but half the values are quoted and some of
> them contain commas. Pull the fields out so I can load them."

## Input

`in/report.txt` — one field per line:

```
name=quarterly report
owner="Ada Lovelace"
note="costs $5,000 and 100% of budget"
```

The file is messy in realistic ways: comment lines, blank lines, quoted values, values
that contain `=`, a value that is empty, a key that repeats, and lines that are not
fields at all.

## Rules

1. **Ignore** a line that is empty or only whitespace, and a line whose first
   non-whitespace character is `#`. Ignored lines are not counted anywhere.
2. Every other line is one field. Split it at the **first** `=`. The text before it is
   the **key**, the text after it is the **value**.
3. Trim whitespace from both the key and the value. A key must be nonempty and may
   contain only letters, digits, `_`, `.` and `-`. A line with no `=`, or with a key that
   breaks that rule, is **invalid**: count it and skip it.
4. If the value starts with `"` **and** ends with `"` (and is at least two characters
   long), it is a **quoted value**: the quotes are removed and the content between them
   is the value, commas and all. Otherwise the value is used as trimmed.
5. A key that appears more than once keeps the **last** value. Every repeat counts as a
   **duplicate**.

## Output

Write exactly these files to `$OUT`:

1. **`out/fields.csv`** — header `key,value`, then one row per distinct key, sorted by
   key ascending in **byte order** (so `a-b` sorts before `ab`). A value that contains a
   comma or a double quote is written in double quotes, with any inner double quote
   doubled; every other value is written bare. The file ends with a newline.
2. **`out/summary.json`** — an object with exactly these keys:
   - `keys` — how many distinct keys the report has (int)
   - `duplicates` — how many times a key repeated (int)
   - `invalid` — how many lines were invalid (int)

   Print it as one compact JSON object: `{"keys":8,"duplicates":1,...}`.

## Messes to expect

- `note="costs $5,000 and 100% of budget"` holds a comma inside quotes, and the value
  must be quoted again in the CSV output
- `tag=a=b` splits at the **first** `=`, so the value is `a=b`
- `quoted="a=b"` is a quoted value, so the `=` inside the quotes is part of the value
- `name` appears twice: the second value wins and the repeat is one duplicate
- `two words=value` and `bad line without equals` are invalid, and a comment line is
  ignored rather than invalid

## Timebox

Four minutes. Lua patterns have no alternation, so try the shapes one at a time
instead of trying to write one clever pattern.
