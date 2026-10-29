# 189-ruby-lazy-pipeline

> "A massive operational log file needs to be triaged for the first few payment incidents.
> Reading the whole file into memory causes OOM in constrained environments; we must stop reading
> the moment we reach our match target."

## Input

`in/stream.log` — timestamped log records:

```
10:00:01 INFO [payment] code=200 ok
10:00:02 WARN [payment] code=404 not found
10:00:03 DEBUG [auth] ping
10:00:04 ERROR [payment] code=500 timeout
10:00:05 WARN [payment] code=429 rate limit
10:00:06 INFO [payment] code=200 ok
10:00:07 ERROR [payment] code=503 unavailable
10:00:08 WARN [payment] code=400 bad request
10:00:09 ERROR [payment] code=500 boom
10:00:10 ERROR [payment] code=500 boom
```

Blank lines and `#` comments are skipped.

## Rules

1. Inspect lines sequentially.
2. Select lines that contain service tag `[payment]` AND have level `WARN` or `ERROR`.
3. Extract:
   - `timestamp` (first token)
   - `level` (second token)
   - `code` (integer digits from `code=(\d+)`)
   - `message` (remainder of line after code value)
4. Take the first **5** matching records.
5. The pipeline must be **lazy**: stop consuming lines immediately once 5 matches are collected.
   Do not read remaining lines to EOF.
6. Track `inspected`: the total number of non-comment, non-empty log lines read before termination.

## Output

Write exactly these files to `$OUT`:

1. **`out/matches.csv`** — header `timestamp,level,code,message`, in stream order.
2. **`out/summary.json`** — keys `inspected`, `matched`, `target`. One compact JSON object:
   `{"inspected":8,"matched":5,"target":5}`.

## Messes to expect

- Reading all lines eagerly (e.g. `File.readlines` or eager `.map.select`) will inspect 10 lines instead of 8.
- Lines from other services (e.g. `[auth]`) must count toward `inspected` but not toward `matched`.

## Timebox

Four minutes. Use `File.open(...).each_line.lazy` with `.take(5).force`.
