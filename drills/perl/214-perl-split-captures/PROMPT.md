# 214-perl-split-captures

> "The access-log importer started writing the wrong columns: the timestamp column came
> out empty and the method column held the timestamp. The splitter had a capture group in
> the pattern — `split /(\\S+)/` — and a pattern with captures returns the captured text
> too, so every field landed in the wrong column."

## Input

`in/access.log` — one access-log record per line: a timestamp, a method, a path and a
status code, separated by whitespace.

```text
2026-10-29T10:00:00 GET /health 200
2026-10-29T10:00:05 POST /api/v1/orders 201
2026-10-29T10:00:09 GET /missing 404
2026-10-29T10:00:14 DELETE /api/v1/orders/7 204
```

## Rules

1. Read `in/access.log`. Skip blank lines. Each record has exactly four fields:
   `timestamp`, `method`, `path`, `status`. Runs of whitespace separate the fields, and
   no field contains whitespace.
2. A record is **ok** when its status begins with `2` (200, 201, 204 ...). Every other
   record is an **error**.
3. **`out/access.csv`** — header `index,timestamp,method,path,status`. One row per
   record, in file order, `index` starting at 1.
4. **`out/summary.json`** — keys `records`, `ok`, `errors`. One compact JSON object.

## Messes to expect

- A `split` pattern that contains a **capture group** returns the captured text as well
  as the pieces around it. `split /(\\S+)/, $line` gives eight fields for a four-field
  line, and every field lands in the wrong column.
- Capture groups are how you keep the separators. For plain fields, use a pattern with
  no capture.
- `split ' '` is awk mode: it splits on runs of whitespace. `split /\\s+/` keeps an
  empty first field when the line starts with whitespace.

## Timebox

Five minutes.
