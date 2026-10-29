# 061-retry-queue

> "These maintenance commands run in order. A temporary `75` happens sometimes;
> retry that, but don't keep hammering a command with a real configuration error."

## Task

Read job names from `in/jobs.txt`. For each job, run:

```bash
bash "$IN/worker.bash" "$job" "$WORK/attempt-state"
```

The worker stores its attempt count in that state directory. Run jobs in input order.

## Rules

1. Skip blank and `#` comment lines. Job names contain lowercase letters only.
2. Give each job at most **three attempts**. Exit `0` succeeds. Exit `75` is
   temporary: retry unless it was attempt three. Every other nonzero exit is final.
3. Capture stdout and stderr separately. The final `message` is the successful
   stdout on success, or the last stderr on failure, with its trailing newline removed.
4. Keep going after a failed job because the requested result is a complete report.
   Show every failure in the report; do not silently treat it as success.
5. No sleeps. The fixture is deterministic, so a delay would only waste the timebox.

## Output

- `out/attempts.csv`: header `job,attempt,exit_code`, one row per invocation, in
  execution order.
- `out/results.csv`: header `job,status,attempts,message`, one row per job in input
  order. `status` is `ok` or `failed`.
- `out/summary.json`: exactly four integers: `jobs`, `ok`, `failed`, `attempts`.

## Messes to expect

- blank and comment lines in the queue
- one job that succeeds immediately, one after one retry, and one after two
- a permanent error that must stop after one attempt
- a transient error that never clears and must stop at the retry ceiling

## Timebox

5 minutes. Put the command in an `if` so `set -e` does not erase its exit status.
