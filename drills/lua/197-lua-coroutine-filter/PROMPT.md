# 197-lua-coroutine-filter

> "A metric aggregator tracks cumulative usage across multiple independent streams.
> We must maintain per-stream accumulator state using bidirectional Lua coroutines
> without polluting global state."

## Input

`in/events.txt` — whitespace-delimited rows of `<stream_id> <delta>`:

```
A 10
B 20
A 25
B 15
A 20
B 30
A 5
```

Blank lines and `#` comments are skipped.

## Rules

1. Define a coroutine factory `make_meter(threshold)`:
   - The coroutine function receives `first_delta` on initial resume.
   - It maintains a running total and yields `(total >= threshold, total)` on each incoming delta.
   - Each subsequent delta is received as the return value of `coroutine.yield()`.
2. For each incoming event in `in/events.txt`:
   - If the stream coroutine does not exist, instantiate it with `threshold = 50` and resume with the initial delta.
   - If the coroutine already exists, resume it passing the new delta.
   - Capture `alert` (`"true"` if total >= 50, else `"false"`) and `sum` (integer running total).
3. Export event results to `out/meter.csv`.

## Output

Write exactly these files to `$OUT`:

1. **`out/meter.csv`** — header `step,stream,delta,sum,alert`, in event arrival order (step starting at 1).
2. **`out/summary.json`** — keys `events`, `streams`, `alerts`, `final_max`. One compact JSON object:
   `{"events":7,"streams":2,"alerts":3,"final_max":65}`.

## Messes to expect

- In Lua, subsequent values passed to `coroutine.resume(co, val)` are returned by `coroutine.yield()`, NOT as new arguments to the main function.
- Coroutines must be preserved per-stream; recreating them on each line resets the total.

## Timebox

Four minutes. Use `coroutine.create` and bidirectional `coroutine.yield` / `coroutine.resume`.
