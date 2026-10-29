# 078-cleanup-budget

> "I have two minutes and I need 3.5 GB free. Give me the deletion order: cheapest risk
> first, and tell me whether it is even enough."

## Task

`in/candidates.csv` lists cleanup targets as `path,size_mb,risk`, where `risk` runs from
1 (regenerable cache) to 5 (real data). `in/target.txt` holds the amount to free, in MB.

## Rules

1. Skip blank lines and lines beginning with `#`. The header row is the one whose
   `size_mb` is not an integer.
2. Order candidates by `risk` ascending, then `size_mb` descending, then `path` ascending
   in byte order.
3. Take candidates in that order until the freed total is **at least** the target. Do not
   take anything after that, even if it would be a better fit.
4. Overshooting is fine. If the list runs out first, plan everything and report
   `complete: false` (this is a report, not a failure - do not exit non-zero).
5. `order` in the output is 1-based in take order.

## Output

- `out/cleanup.csv` - header `order,path,size_mb,risk`, only the taken rows.
- `out/summary.json` - exactly four keys: `target_mb`, `freed_mb` (both integers),
  `taken`, and `complete` (a boolean).

## Messes to expect

- `risk` alone does not decide order: the biggest cache does not necessarily go first
- a large low-risk directory that would overshoot by itself
- candidates sorted in the file by size, not by risk

## Timebox

3 minutes. Sort with three keys, walk once, stop on the threshold.
