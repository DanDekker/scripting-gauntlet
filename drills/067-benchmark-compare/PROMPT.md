# 067-benchmark-compare

> "The new build is benchmarked on three OSes. Compare it with the baseline and flag
> any case that's more than 10% slower."

## Task

`in/baseline.csv` and `in/candidate.csv` contain repeated timings in milliseconds, with
header `platform,case,run,ms`. Each platform/case pair has exactly three runs in each
file. Compare the median candidate time with the baseline median.

## Rules

1. Match rows by `platform` and `case`; run number only identifies a sample.
2. Both files must contain the same platform/case pairs and exactly three positive
   timings for each pair. On a mismatch, name the pair on stderr and exit non-zero.
3. `change_pct` is `(candidate_median - baseline_median) / baseline_median * 100`,
   rounded to one decimal. A positive value means slower.
4. `status` is `regression` only when `change_pct > 10.0`; exactly 10.0 is `ok`.
5. Sort output by platform then case, both ascending in byte order.

## Output

**`out/comparison.csv`** — header `platform,case,baseline_median_ms,candidate_median_ms,change_pct,status`, one row per pair.

**`out/summary.json`** — exactly `comparisons`, `regressions`, and `threshold_pct`.

## Messes to expect

- rows in each input are not sorted
- three samples vary; use the median rather than the first or last run
- Windows has a 10% slowdown exactly on the threshold
- one Linux gzip case regresses by 20%; a fast result elsewhere must not hide it

## Timebox

4 minutes. Group each file by platform and case, sort the three numbers, then compare.
