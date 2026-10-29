# 066-benchmark-runner

> "I want a repeatable microbenchmark script I can use on Linux, macOS, and Windows.
> Run the suite, throw away warmups, and give me timings I can compare later."

## Task

`in/config.json` declares benchmark case names, warmup count, sample count, and loop
size. Run each case as a child process:

```text
python workload.py <case> <iterations>
```

Use `python3`, `python`, or `py -3` as available.

## Rules

1. Run each case's warmups first; do not include them in reported samples.
2. Measure child wall time with a monotonic clock. The measurement includes interpreter
   startup and the child process.
3. A nonzero exit or a different checksum between runs is an error: name the case on
   stderr and exit non-zero.
4. For each case, calculate the median and nearest-rank p95. With five samples, p95 is
   the largest sample. Round both timings to six decimal places.
5. Sort cases by name ascending.

## Output

- `out/samples.csv`: header `case,run,seconds,checksum`; one row per measured run,
  sorted by case then run number.
- `out/summary.csv`: header `case,samples,median_seconds,p95_seconds,checksum`, one row
  per case, sorted by case.
- `out/summary.json`: exactly `cases`, `warmups_per_case`, and `samples_per_case`.

## Messes to expect

- startup runs are warmups and must not inflate the sample count
- both implementations produce the same checksum but have different runtimes
- process startup is part of the measurement

## Timebox

5 minutes. Keep the workload fixed; the point is to build a sound runner, not to tune
the code under test.
