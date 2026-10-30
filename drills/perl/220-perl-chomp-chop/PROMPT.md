# 220-perl-chomp-chop

> "The last note in the file came out as `gamm`. The importer used `chop` to strip the
> newline — but `chop` removes the last character whatever it is, and the last line of
> the file has no newline to remove, so it lost its `a`."

## Input

`in/notes.txt` — three notes. The file ends **without** a trailing newline, so the last
line has no terminator:

```text
alpha
bravo
gamma
```

## Rules

1. Read `in/notes.txt` as three records: `alpha`, `bravo`, `gamma`. Every character of
   every record is part of the record — nothing may be dropped.
2. For each record, report its text and its length in characters.
3. **`out/notes.csv`** — header `index,text,length`. One row per record, in file order,
   `index` starting at 1.
4. **`out/summary.json`** — keys `notes`, `chars`, `last`. One compact JSON object.
   - `notes` — the number of records.
   - `chars` — the total number of characters across all the records (line terminators
     are not part of a record).
   - `last` — the text of the last record.

## Messes to expect

- `chomp` removes the input record separator (`$/`, a newline by default). On the last
  line there is no newline, so `chomp` removes nothing — which is what you want.
- `chop` removes the **last character**, whatever it is. On the first two lines that
  happens to be the newline, so it looks right; on the last line it eats a real
  character of the record.
- Strip the terminator with `chomp`, not `chop`.

## Timebox

Four minutes.
