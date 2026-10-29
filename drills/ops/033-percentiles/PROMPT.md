# 033-percentiles

> "Dashboards lie about latency. Give me p50, p90 and the max per endpoint, straight from the log."

## Task

`in/latency.csv` has `endpoint,ms` rows — one per request.

## Rules

1. `endpoint` is trimmed and lowercased; `ms` is an integer, trimmed.
2. Percentiles use **nearest-rank**: sort the endpoint's values ascending, and the p-th
   percentile is the value at 1-based index `ceil(p/100 * n)`. No interpolation, no averaging.
   With `n = 5`, p50 is the 3rd smallest and p90 is the 5th.
3. `count`, `p50`, `p90`, `max` are all integers.
4. Endpoints sort ascending. An endpoint with a single sample repeats that sample in every
   column.

## Output

**`out/latency.csv`** — header exactly `endpoint,count,p50,p90,max`, one row per endpoint,
sorted by `endpoint` **ascending**.

**`out/summary.json`** — exactly three keys: `endpoints`, `requests` (total samples), `slowest`
(the largest `ms` seen anywhere).

## Messes to expect

- a padded duration (` 42 `)
- one endpoint with a single sample
- sample counts that are not multiples of ten, so the index should be rounded **up**
- the same endpoint spelled in two cases

## Timebox

3 minutes. Sort by endpoint then duration, then index into each run.
