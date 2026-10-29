# 007-quoted-fields

> "Note column has commas, quotes, and sometimes line breaks in it. I need it intact."

## Task

`in/notes.csv` is a CSV with quoting that actually means something. Parse it and write it
back out as valid CSV.

## Rules

1. A field may be wrapped in double quotes. Inside a quoted field, `""` means one literal
   `"` and a comma or newline is just a character.
2. A quoted field may contain a **newline**, so one record can span several lines.
3. Output must be valid CSV: quote any field containing a comma, a quote, or a newline,
   and double any quotes inside it.

## Output

**`out/clean.csv`** — the header and all four rows, re-emitted as valid CSV.

**`out/stats.json`** — exactly two keys: `rows` (data rows) and `multiline` (the number
of **fields** whose value contains a newline).

## Messes to expect

- `She said ""hi""` is one field, not three
- one field contains a real line break, so the file has 5 physical lines and 4 records

## Timebox

5 minutes. python's `csv` module does this in three lines. If you are writing a parser in
awk, that is allowed and instructive — but it must handle the embedded newline.
