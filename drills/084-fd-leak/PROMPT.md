# 084-fd-leak

> "Something is leaking file descriptors again. I have periodic samples from each pid -
> tell me which one is climbing and how fast, and do not cry leak at normal churn."

## Task

`in/fd-samples.csv` has `sample,pid,fds`, one row per reading. `sample` is a minute
number, so two consecutive samples are one minute apart. Rows are not grouped.

## Rules

1. Skip the header row and blank lines. Group rows by `pid`, ordered by `sample`.
2. `fds_per_min` is `(last_fds - first_fds) / (last_sample - first_sample)`, one decimal.
   Missing sample numbers are fine: the span comes from the samples you actually have.
3. `monotonic` is `true` only when no sample is lower than the one before it.
4. A pid is `leaking` when it is monotonic **and** `fds_per_min >= 5.0`.
5. A pid with fewer than two samples cannot be measured: skip it and count it in
   `skipped`.
6. Sort rows by `fds_per_min` descending, then `pid` ascending.

## Output

- `out/leaks.csv` - header `pid,first_fds,last_fds,fds_per_min,monotonic`, one row per
  measured pid. `monotonic` is `true` or `false`.
- `out/summary.json` - exactly three integers: `pids`, `leaking`, `skipped`.

## Messes to expect

- a pid whose count dips, which is churn rather than a leak
- a fast climber that must be flagged
- a pid with a single sample at the end of the file
- samples interleaved across pids

## Timebox

3 minutes. Sort by pid then sample, walk each group once.
