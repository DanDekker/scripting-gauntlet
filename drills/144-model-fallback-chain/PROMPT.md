# 144-model-fallback-chain

> "Our router is supposed to retry a tier, then fall through to the next one. Here are
> yesterday's simulated attempts. Tell me where each task actually landed, how many
> attempts it cost, and the latency we paid — and remember a 200 that took longer than
> the tier's timeout is still a failure."

## Input

- `in/tasks.jsonl` — one JSON object per line: `{"task_id": "t1", "prompt_len": 500, "priority": "high"}`.
  Lines that are blank, not JSON, not an object, or without a `task_id` are skipped.
- `in/providers.json` — a JSON array of tiers, in any order:
  `[{"tier": 1, "model": "primary", "timeout_ms": 2000, "max_retries": 1}, ...]`
- `in/attempts.csv` — header `task_id,tier,attempt,status,latency_ms`. `status` is a
  simulated HTTP-ish outcome (`200`, `429`, `500`, `504`), `attempt` is 1-based within a
  tier. Rows may be in any order. Malformed rows (not five integer-ish cells) and rows for
  a `task_id` that is not in `tasks.jsonl` are ignored.

## Rules

1. Tiers are tried in **increasing `tier`** (1, 2, 3, ... as listed in `providers.json`).
2. Within a tier, attempts are tried in **increasing `attempt`**, from 1 up to
   **`1 + max_retries`** of that tier. Recorded rows beyond that budget are ignored
   (tier 3 has `max_retries = 0`, so only attempt 1 counts there).
3. An attempt **succeeds** only when `status == 200` **and** `latency_ms <= timeout_ms`
   for that tier. A `200` slower than the timeout is a timeout failure.
4. First success wins: `outcome = success`, the resolved tier is that tier, and the task
   stops — later tiers and later attempts are not made.
5. A failed attempt is retried on the same tier while the budget allows. If the budget runs
   out **or** a needed attempt number has no recorded row, the tier is exhausted and the
   task falls back to the next tier.
6. When no tier succeeds, `outcome = failed` with an **empty** resolved tier.
7. `attempts_count` is the number of attempts actually made, and `total_latency_ms` is the
   sum of their latencies across every tier visited — failed attempts included. A task
   with no recorded attempts is `failed` with `0` attempts and `0` ms.

## Output

Write exactly these files to `$OUT`:

1. **`out/resolutions.csv`** — header `task_id,outcome,resolved_tier,attempts_count,total_latency_ms`.
   One row per task in `tasks.jsonl`, sorted by `task_id` ascending (plain string order).
   `outcome` is `success` or `failed`; `resolved_tier` is the tier number as a string, or
   empty for a failed task.
2. **`out/summary.json`** — object with exactly these keys:
   - `total_tasks` (int)
   - `success_count` (int)
   - `failed_count` (int)
   - `fallback_invoked` — tasks that resolved on a tier **greater than 1** (int)
   - `total_latency_ms` — sum of every task's `total_latency_ms` (int)

## Messes to expect

- `t4` fails on a `200` that took 2500 ms against a 2000 ms timeout, then succeeds at 1900 ms
- `t7` lands on exactly 2000 ms, which is **not** over the 2000 ms timeout -> success
- `t3` burns both tier-1 attempts (`500`, `504`), then its tier-2 `200` at 3200 ms is a
  timeout too, and only the retry at 900 ms resolves it
- `t6` exhausts everything and its `t6,3,2,200,100` row is beyond tier 3's retry budget, so
  it is failed with 5 attempts and 3610 ms, not 6 attempts
- `t5` has no attempts at all -> `failed`, empty tier, 0 attempts, 0 ms
- `t9` has only attempt 1 recorded on tier 1, so the tier is exhausted early and it falls
  through to tier 2
- `t99,1,1,200,50` belongs to no task in `tasks.jsonl` and is ignored; `t10` is not valid
  JSON and is not a task
- the attempt rows are shuffled, so "next attempt" means the next `attempt` number, not
  the next file line

## Timebox

About five minutes. If you are past that, the approach is wrong.
