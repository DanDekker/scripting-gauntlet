# 002-log-triage

> "Can you tell me what the traffic actually looked like in this window? Status code
> spread, and which endpoints people hit. There's a bit of garbage in there."

## Task

`in/access.log` is a slice of an nginx access log in combined format:

```
10.0.0.5 - - [29/Oct/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 5120 "-" "Mozilla/5.0"
```

Parse it and report.

## Rules

1. A record is the `"METHOD PATH PROTOCOL"` field followed by the **status** after the
   closing quote. Anything that does not match that shape is **skipped and counted** —
   not fatal.
2. **Strip the query string** from the path before grouping: `/api/users?page=2` counts
   as `/api/users`.
3. Count statuses and paths over the whole file. Keep all statuses; keep the **top 5**
   paths only.

## Output

**`out/status.csv`** — header, then one row per status code present:

```
status,count
200,7
```

Ordered by `count` **descending**, ties broken by `status` **ascending** (numeric).

**`out/top_paths.csv`** — header, then at most 5 rows:

```
path,hits
/some/other/path,12
```

Ordered by `hits` **descending**, ties broken by `path` **ascending** (bytes).

**`out/summary.json`** — exactly two keys: `valid` (records parsed) and `skipped`
(lines that did not parse).

## Messes to expect

- at least one line that is not a log record at all
- query strings that differ only by page number
- duplicate hits on the same path from different clients
- statuses that are not `200`

## Timebox

3 minutes. awk with `"` as a field separator is the fast answer; a regex is the portable one.
