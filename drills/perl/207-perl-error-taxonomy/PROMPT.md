# 207-perl-error-taxonomy

> "Our probe runner blamed the wrong thing. It reported the exit code 768 for a job that
> exited 3, it reported a stale errno for a file that opened fine, and it reported an
> empty message for a `die`. Each failure lives in its own variable."

## Input

`in/probes.csv` — header `id,kind,arg`:

```csv
id,kind,arg
1,exit,3
2,exit,0
3,die,disk full
4,open,missing/report.txt
5,exit,42
6,die,timeout
7,open,present.txt
```

`in/present.txt` exists. `in/missing/report.txt` does not.

## Rules

1. For each probe, in file order, perform the operation named by `kind`:
   - `exit` — run the child process
     `python3 -c "import sys; sys.exit(int(sys.argv[1]))" <arg>`
     and read the status it exited with.
   - `die` — evaluate `die "<arg>\n"` inside an `eval` block and read the message it
     raised.
   - `open` — try to open `in/<arg>` for reading.
2. Report `status`:
   - `exit` — `ok` when the child's exit code is 0, otherwise `failed`.
   - `die` — `failed`.
   - `open` — `ok` when the file could be opened, otherwise `failed`.
3. Report `detail`:
   - `exit` — the child's **exit code** as a whole number.
   - `die` — the message the `die` raised, without its trailing newline.
   - `open` — `0` when the file opened, and the **errno number** when it did not.
4. Read each failure from the variable that holds it: the child's exit code from `$?`,
   the errno from `$!`, the raised message from `$@`. `$?` holds a *wait status*, so
   the exit code is `$? >> 8`. `$!` is only meaningful immediately after the failed
   call, and `$@` is only meaningful until the next `eval`.
5. **`out/results.csv`** — header `id,kind,status,detail`. One row per probe, in file
   order.
6. **`out/summary.json`** — keys `probes`, `failed`, `ok`. One compact JSON object.

## Messes to expect

- `system()` returns the raw wait status. A child that exits 3 comes back as `768`,
  and `768 >> 8` is the exit code you want.
- `$!` keeps its old value after a call that *succeeded*. For a file that opened, the
  errno is `0` — do not report whatever was left over.
- `eval` clears `$@` on success, so capture the message before running anything else.

## Timebox

Five minutes. One variable per kind of failure: `$?` for children, `$!` for system
calls, `$@` for `eval`.
