# 221-perl-printf-list

> "The report had one line in it — `alpha` — and a warning about a redundant argument.
> The writer did `printf \"%s\\n\", @records;`, but `printf` applies its format **once**
> and treats the rest of the list as spare arguments."

## Input

`in/records.txt` — one record per line:

```text
alpha
bravo
charlie
```

## Rules

1. Read `in/records.txt`, one record per line, in file order. Skip blank lines.
2. **`out/report.txt`** — **one line per record**: each record followed by a newline, in
   file order. Three records means three lines.
3. **`out/summary.json`** — keys `records`, `lines`, `last`. One compact JSON object.
   - `records` — the number of records read.
   - `lines` — the number of lines written to `out/report.txt`.
   - `last` — the text of the last record.

## Messes to expect

- `printf FORMAT, LIST` passes every element of `LIST` as a **separate argument**.
  `printf "%s\n", @records` uses the first record for the conversion and calls the rest
  redundant, so one line is written and perl warns about it.
- `printf "%s\n", $_ for @records` calls `printf` once per record and writes one line
  each.

## Timebox

Four minutes.
