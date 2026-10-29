# 172-lua-coroutine-pipeline

> "The stream is bigger than memory, one line in the middle has a garbage amount, and the
> totals must not quietly include the lines after it."

## Input

`in/stream.log` — one record per line:

```
user level amount
alice info 10
```

## Rules

1. Read the file in **chunks of 4096 bytes** and split the buffer into lines, carrying any
   partial line across the chunk boundary. Do not assume one line per read.
2. A record is three whitespace-separated fields: user, level, amount.
3. Sum `amount` per level and count the records per level.
4. A line whose `amount` is not a number is **fatal**: the run aborts at that line. Totals
   include only the records before it, and the summary names the line number.
5. Sort the output by level ascending in byte order.

## Output

Write exactly these files to `$OUT`:

1. **`out/totals.csv`** — header `level,total,count`, one row per level seen before the
   abort.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — lines consumed, including the fatal one (int)
   - `processed` — records aggregated (int)
   - `aborted` — 1-based line number of the fatal record, or `null` when the file ended
     cleanly (int or null)
   - `levels` — rows in `totals.csv` (int)

   Print it as one compact JSON object: `{"lines":6,"processed":5,"aborted":6,"levels":3}`.

## Messes to expect

- the sixth line has `x` where the amount should be: the run stops there
- `info` appears three times before the abort, `warn` once, `error` once
- the file ends with a newline, so the last chunk leaves an empty buffer, not an empty line
- after the error the coroutine is dead; resuming it again must not happen

## Timebox

Five minutes. `pcall` around the consuming loop, not around each line: the first bad record
ends the run.
