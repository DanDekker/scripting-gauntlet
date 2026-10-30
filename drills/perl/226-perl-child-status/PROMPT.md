# 226-perl-child-status

> "Our health check said every step passed. One step was killed by SIGKILL and another
> tried to run a binary that isn't installed — both looked like exit code 0."

## Input

`in/probes.csv` — header `id,kind,arg`:

```csv
id,kind,arg
1,exit,0
2,exit,3
3,exit,42
4,signal,9
5,signal,15
6,missing,no-such-command-xyz
```

## Rules

1. Read `in/probes.csv`. For each probe, in file order, run the probe:
   - `exit` with arg `N` — run the child
     `python3 -c "import sys; sys.exit(int(sys.argv[1]))" N`.
     The child exits with status `N`.
   - `signal` with arg `N` — run the child
     `python3 -c "import os, signal, sys; os.kill(os.getpid(), int(sys.argv[1]))" N`.
     The child kills itself with signal `N`.
   - `missing` with arg `NAME` — run the program `NAME` directly, with no shell. The
     program does not exist.
2. Report `status` for each probe:
   - `ok` — the child ran and exited with status 0.
   - `failed` — the child ran and exited with a non-zero status.
   - `signalled` — the child was killed by a signal.
   - `notfound` — the program could not be executed at all.
3. Report `detail` for each probe:
   - `ok` and `failed` — the child's exit status.
   - `signalled` — the signal number that killed the child. A shell reports
     `128 + signal`; report the signal itself.
   - `notfound` — `-1`.
4. **`out/results.csv`** — header `id,kind,status,detail`. One row per probe, in file
   order.
5. **`out/summary.json`** — keys `probes`, `ok`, `failed`, `signalled`, `notfound`. One
   compact JSON object.

## Messes to expect

- `system` returns the **wait status**, not the exit code: a child that exited 3 comes
  back as `768`. The exit code is `$? >> 8`.
- A child killed by a signal leaves the signal in the low bits of `$?` and an exit code
  of 0, so `$? >> 8` alone says "success". The signal is `$? & 127`.
- When the program cannot be executed, `system` returns `-1` and `$?` is `-1`; shifting
  that gives a nonsense number, so check for the failure first.
- The shell's `128 + signal` convention is not what `system` gives you.

## Timebox

Five minutes.
