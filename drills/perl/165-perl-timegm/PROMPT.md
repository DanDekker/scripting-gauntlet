# 165-perl-timegm

> "Six services stamp their logs with UTC. I need epoch seconds so I can sort them, and I
> need the impossible dates rejected instead of silently rolled forward."

## Input

`in/stamps.txt` — one stamp per line, in this exact shape:

```
YYYY-MM-DDTHH:MM:SSZ
2026-10-29T12:00:00Z
```

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#`.
2. A stamp is valid only when it matches `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$`
   **and** names a real UTC instant: month 1–12, day valid for that month and year
   (leap years included), hour 0–23, minute 0–59, second 0–59. `2026-02-30T00:00:00Z` is
   invalid, `2024-02-29T00:00:00Z` is valid.
3. `epoch` is the number of UTC seconds since `1970-01-01T00:00:00Z`. Epoch `0` is a real
   answer.
4. Sort by `epoch` **ascending**.

## Output

Write exactly these files to `$OUT`:

1. **`out/epochs.csv`** — header `stamp,epoch`, one row per valid stamp, sorted by epoch
   ascending. The stamp is written exactly as it appeared, trimmed.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — non-blank lines (int)
   - `valid` — rows in `epochs.csv` (int)
   - `invalid` — rejected lines (int)
   - `first` — the smallest epoch, or `""` when nothing parsed (int or string)
   - `last` — the largest epoch, or `""` (int or string)

   Print it as one compact JSON object: `{"lines":7,"valid":5,...}`.

## Messes to expect

- `1970-01-01T00:00:00Z` is epoch `0`, which is falsy in perl — `if ($epoch)` would drop it
- `2024-02-29T00:00:00Z` is a real leap day; `2026-02-30T00:00:00Z` is not a date
- `not-a-stamp` fails the shape and is counted, not guessed at
- months are 0-based in perl's time functions: October is `9`, not `10`
- a year passed as years-since-1900 is ambiguous in `Time::Local`: 70 means 2070, not 1970

## Timebox

Four minutes. Build the instant, then prove it: `gmtime` of your epoch must give the same
fields back, or the date was not real.
