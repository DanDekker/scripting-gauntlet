# 107-backoff-plan

> "The client retries everything and it retries badly — we hammered a rate limiter for two
> minutes last night. Out of this request log, tell me what we should have retried, and with
> what waits."

## Input

`in/requests.log` — one request per line:

```
2026-10-29T10:00:00Z POST /v1/chat 503 upstream_unavailable
2026-10-29T10:00:05Z POST /v1/chat 200 ok
```

`in/config.json` — `{"base_seconds": 2, "max_attempts": 5}`.

`in/requests.log` is messy in realistic ways: a blank line, a line with only three fields,
prose that is not a log line at all, a line with several spaces or a tab between fields, a
line with a reason that contains spaces (`timeout after 30s`), a line with no reason at all
(`... 500` and then nothing), a `302`, a `404`, a `2xx` that is not `200`, and the same
request appearing more than once.

## Rules

1. **A valid line** has at least four whitespace-separated fields:
   `<timestamp> <method> <path> <status> [<reason>]`. Fields may be separated by any run of
   spaces or tabs. A line with fewer than four fields, and a blank line, is skipped — it is
   not a request and counts nowhere. The reason is optional and may contain spaces; it is
   never used for anything except being there.
2. **Each line is one request.** Nothing is grouped: two identical `POST /v1/chat 503` lines
   are two requests with two independent schedules, and each starts again at attempt 1.
3. **Classify the status** (the numeric value of the fourth field):
   - `200`-`299` — **success** (counted, never retried)
   - `429` — **RATE_LIMITED**, retryable
   - `500`-`599` — **SERVER_ERROR**, retryable
   - anything else — a **client error** (`302`, `400`, `404`, ...): counted, never retried
   A fourth field that is not a number is a client error too.
4. **Backoff** for a retryable request, with `base = config.base_seconds` and
   `max = config.max_attempts`: the request is attempted once, then retried up to `max - 1`
   times. Retry `k` (1-based) waits `base * 2^(k-1)` seconds before it happens, so with
   `base = 2` the waits are 2, 4, 8, 16.
5. **Exhausted.** A retryable request is exhausted when its total attempts (`1 + retries`)
   reach `max_attempts`. With this config every retryable request runs the full schedule, so
   `exhausted` equals `retryable` — compute both rather than assume.

## Output

Write exactly these files to `$OUT`:

1. **`out/schedule.csv`** — header `request,attempt,wait_seconds`. One row per retry of a
   retryable request:
   - `request` is the request's `<method> <path> <status>` joined by single spaces, exactly
     as those three fields appear (so `POST /v1/chat 503`), never the timestamp or reason
   - `attempt` is the retry number, starting at 1
   - `wait_seconds` is the wait before that retry
   Rows are ordered by the request's position in the log first — an earlier request's retries
   all come before a later request's — then by `attempt` ascending. A non-retryable request
   contributes no rows.
2. **`out/summary.json`** — an object with exactly these keys, all ints:
   - `requests` — valid lines
   - `success` — 2xx
   - `retryable` — `429` or 5xx
   - `client_errors` — everything else (`success + retryable + client_errors == requests`)
   - `retries` — rows in `out/schedule.csv`
   - `exhausted` — retryable requests whose total attempts reached `max_attempts`
   - `total_wait` — sum of every `wait_seconds` in `out/schedule.csv`

## Messes to expect

- `... POST /v1/chat 500` with nothing after the status is a valid request, not a skip
- `... GET /health 302 redirect` is a client error: no retries
- `... DELETE /v1/session 404 not_found` is a client error: no retries
- `... GET /v1/models 299 throttled_but_served` is a success: no retries
- `... POST /v1/embed 504 timeout after 30s` is retryable even though the reason has spaces
- the two `POST /v1/chat 503` lines are two separate requests, each with its own four rows,
  listed in the order they appear in the log
- the blank line, the three-field line and the prose line are skipped, so `requests` is
  smaller than the number of lines in the file

## Timebox

Five minutes. If you are past that, the approach is wrong.
