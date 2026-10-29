# 136-log-anomaly

> "Every minute our agent fleet reports requests and errors. A single bad minute is
> normal. A minute that is *two and a half times worse than the last five* is not — tell
> me which minutes those were and what the error was, so I know who to page."

## Input

- **`in/traffic.csv`** — header `minute,requests,errors,top_error`, one row per minute in
  chronological order:

  ```
  2026-10-29T10:00:00Z,120,2,RateLimitError
  2026-10-29T10:01:00Z,135,1,ConnectionReset
  ```

- **`in/thresholds.json`** — `{"window": 5, "min_requests": 50, "rate_multiplier": 2.5, "min_rate": 0.05}`
  (read the values from the file; do not hardcode them).

## Rules

1. **Parsing.** Blank lines are skipped. A row whose `requests` or `errors` is not a
   non-negative integer (empty, blank, non-numeric) is skipped **and is not a minute**: it
   does not count in `total_minutes`, does not enter the history, and does not shift the
   window. `minute` is taken as-is (trailing whitespace trimmed); `top_error` may be
   empty.
2. **Error rate** of a minute is `errors / requests`, or `0.0` when `requests == 0`.
3. **Baseline.** The window is the `window` **previous** minutes — the current minute is
   never part of its own baseline. Every prior minute counts, including minutes with too
   little traffic. The baseline is the **ratio of sums**: `sum(errors) / sum(requests)`
   over the window, or `0.0` when the window's requests sum to 0. It is *not* the mean of
   the per-minute rates.
4. **Evaluated minute.** A minute is evaluated iff at least `window` minutes came before it
   AND `requests >= min_requests`. Minutes that fail this are not evaluated and not
   counted in `evaluated_minutes`, but they still become history for later minutes.
5. **Anomaly.** An evaluated minute is an anomaly iff **all** of:
   - `error_rate >= min_rate`,
   - `error_rate >= baseline * rate_multiplier`.
6. **Culprit.** The anomaly's `culprit` is its `top_error`. When `top_error` is empty (or
   missing) the culprit is the literal string `Unknown` — never an empty cell.

## Output

1. **`out/anomalies.csv`** — header `minute,requests,errors,error_rate,baseline_rate,culprit`.
   One row per anomaly, in chronological (input) order. `error_rate` and `baseline_rate`
   are always 4 decimals (`0.2000`, `0.0324`); `requests` and `errors` are integers.
2. **`out/summary.json`** — object with exactly these keys:
   - `total_minutes` (int) — minutes that survived parsing
   - `evaluated_minutes` (int) — minutes judged against a baseline
   - `anomaly_minutes` (int)
   - `top_culprit` (string) — the culprit responsible for the most anomaly minutes; ties go
     to the alphabetically smallest name; `""` (empty string) when there are no anomalies.

## Messes to expect

- One minute has `requests = 0` and `errors = 0`: rate `0.0`, not a division error, not a
  gap in the history.
- Two minutes have fewer than `min_requests`: they are never anomalies themselves, yet
  they still push the baseline of the minutes that follow them (a low-traffic minute full
  of errors inflates the denominator's *rate*, deflating the next baseline).
- One minute has a blank `top_error` and **is** an anomaly — its culprit is `Unknown`.
- One minute clears `min_rate` and the multiplier but is not the biggest of the day; being
  a spike is relative, not absolute.
- The spike on `10:05` is followed by four ordinary minutes: the baseline stays poisoned for
  a while, so the minutes right after it are *not* anomalies.
- Three culprits occur once each — `top_culprit` is decided by the tie-break, and
  `RateLimitError` wins because `R` < `T` < `U`.

## Timebox

A few minutes. If you are past that, the approach is wrong.
