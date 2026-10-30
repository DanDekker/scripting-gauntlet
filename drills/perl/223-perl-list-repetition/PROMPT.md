# 223-perl-list-repetition

> "The export came out as a single line: `alpha betaalpha betaalpha beta`. The exporter
> did `my @rows = $template x $count;` — but `x` repeats a **scalar** by concatenating
> the string, so the whole thing stayed one element."

## Input

`in/spec.txt` — two `key=value` lines:

```text
count=3
template=alpha beta
```

## Rules

1. Read `in/spec.txt`. It holds:
   - `count` — a whole number, the number of rows to produce;
   - `template` — the text of one row (the rest of the line after the first `=`).
2. **`out/report.txt`** — exactly `count` lines, each one the template text and nothing
   else. `count` rows means `count` lines. When `count` is `0` the file is empty.
3. **`out/summary.json`** — keys `count`, `lines`, `chars`. One compact JSON object.
   - `count` — the number of rows requested.
   - `lines` — the number of lines written to `out/report.txt`.
   - `chars` — the total number of characters across those lines, **not counting the
     line terminators**.

## Messes to expect

- `x` repeats its left operand. With a **scalar** on the left it repeats the string,
  so `my @rows = $template x $count;` gives **one** element holding the template
  concatenated `count` times.
- With a **list** on the left it repeats the list, so `my @rows = ($template) x $count;`
  gives `count` elements — one per row.
- The string form is right for a run of dashes (`print "-" x 80`); the list form is
  right for a run of rows.

## Timebox

Four minutes.
