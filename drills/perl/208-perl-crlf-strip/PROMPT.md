# 208-perl-crlf-strip

> "The sensor feed is written on Windows, so every line ends with CRLF. Our importer
> used `chomp`, which removes the newline but leaves the carriage return — and the
> carriage return stuck to the end of the value, so every reading failed validation."

## Input

`in/measurements.csv` — a **CRLF** file (each line ends `\r\n`):

```csv
sensor,label,value
s1,room a,21.5
s2,room b,19.0
```

## Rules

1. Read `in/measurements.csv`. The first line is the header.
2. Each later line has three comma-separated fields: `sensor`, `label`, `value`.
3. The file uses CRLF line endings. The carriage return is part of the line terminator,
   not part of the last field — strip the terminator completely.
4. Validate the `value` field against the anchored pattern `^[0-9]+\.[0-9]+$`:
   - `ok` when the value matches exactly,
   - `malformed` otherwise.
5. **`out/readings.csv`** — header `sensor,label,value,status`. One row per reading, in
   file order.
6. **`out/summary.json`** — keys `readings`, `valid`, `malformed`. One compact JSON
   object.

## Messes to expect

- `chomp` removes `$/`, and `$/` is a newline. On a CRLF file that leaves the `\r` on
  the end of the line, and the last field inherits it.
- `"21.5\r"` does not match `^[0-9]+\.[0-9]+$` — the anchor is doing its job.

## Timebox

Four minutes. Strip the whole terminator, not just the newline.
