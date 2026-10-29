# 083-lock-counter

> "Four of my workers keep a shared counter and it drifts. Run four of them at once and
> prove the total is exactly what it should be."

## Task

Write a script that starts **four workers concurrently**. Each worker increments the shared
counter in `out/counter.txt` **50 times**. The starting value is `0`.

## Rules

1. All four workers must actually run at the same time; do not loop over them one by one.
2. Every increment must be read-modify-write **under an exclusive lock** that works across
   processes (an atomic `mkdir` lock or `flock` on a lock file). A bare read-then-write can
   interleave and lose updates, and the check below is exact.
3. If a worker cannot take the lock within a few seconds, or any worker exits non-zero, the
   whole run fails loudly.
4. Each increment appends one line to `out/events.log` containing the worker id (`0`-`3`).
5. The lock file/directory must be removed when the run ends.

## Output

- `out/counter.txt` - the final integer, with a trailing newline.
- `out/events.log` - exactly 200 lines, each `0`, `1`, `2` or `3`.
- `out/summary.json` - exactly three integers: `workers`, `per_worker`, `total`.

## Messes to expect

- four processes contending for the same tiny critical section
- a counter file that must be re-read inside the lock every time
- the temptation to keep the value in a shell variable, which is not shared

## Timebox

5 minutes. One lock helper, one worker function, four background jobs, `wait` on each pid.
