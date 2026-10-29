# 130-rate-limit-headers

> "The vendor kept 429-ing me and I captured the traffic. Read the headers back: for each
> response, am I allowed to keep going, and if not, how long do I sit out? If the answer
> is 'no idea', say that instead of inventing a number."

## Input

`in/responses.log` — captured HTTP responses, one block after another:

```
GET /v1/items HTTP/1.1
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1767225600
```

`in/now.txt` — one integer: the current UNIX epoch seconds, used as the reference time.

## Rules

1. **A block** starts at a line that is a request line: `<METHOD> <path> HTTP/<version>`,
   where the method is uppercase letters only. Everything up to the next request line or
   EOF belongs to that block. Blank lines inside a block are ignored. Lines before the
   first request line belong to no block and are ignored.
2. **The status line** is the first line in the block that starts with `HTTP/`. A block
   with no status line is **skipped** and counted once in `skipped`. The status code is
   the three-digit number after the `HTTP/<version>` token (`^HTTP/[0-9.]+ +([0-9]{3})`).
3. **Headers** are the lines after the status line of the form `Name: value`. Header names
   are matched **case-insensitively** and the value is trimmed. When the same header
   appears more than once in a block, the **last** value wins.
4. **A response is blocked** when its status is `429`. **Exhausted** means not blocked and
   `X-RateLimit-Remaining` is exactly `0` — the next call will be refused.
   `X-RateLimit-Remaining` that is missing, negative or not an integer is unknown, not
   exhausted.
5. **The wait** is computed only for a blocked response; for every other response there is
   no wait to report. In order:
   1. `Retry-After` present and an integer (`^[0-9]+$`) → that number of seconds.
   2. `Retry-After` present and an RFC 1123 HTTP-date (`Thu, 01 Jan 2026 00:01:00 GMT`)
      → seconds from `now` until that instant, **clamped to 0** when it is in the past.
   3. `X-RateLimit-Reset` present and an integer → `reset - now`, clamped to 0.
   4. none of the above → the wait is **unknown**. A `Retry-After` that is neither an
      integer nor a parseable date is treated as absent and falls through to
      `X-RateLimit-Reset`.
   A known wait of `0` is a known wait — it is reported as `0`, not as unknown.

## Output

**`out/responses.csv`** — header `status,remaining,wait,action`, then one row per block
that had a valid status line, in input order.

- `status` — the status code, as an integer.
- `remaining` — `X-RateLimit-Remaining` as an integer, or **empty** when unknown.
- `wait` — the wait in seconds as an integer, or **empty** when unknown or when the
  response is not blocked.
- `action` — exactly one of:
  - `wait` — blocked and the wait is known
  - `wait-unknown` — blocked and the wait cannot be determined
  - `hold` — not blocked but the quota is exhausted
  - `proceed` — anything else

**`out/summary.json`** — an object with exactly these keys:

| key | meaning |
|---|---|
| `responses` | blocks with a valid status line (= rows in `responses.csv`) |
| `skipped` | blocks with no status line |
| `blocked` | responses whose status is 429 |
| `exhausted` | responses that are not blocked but whose remaining is 0 |
| `total_wait` | sum of the known waits (`0` when none are known) |

## Messes to expect

- a 429 with **no** `Retry-After` and **no** `X-RateLimit-Reset` — the wait is unknown
- a 429 with `retry-after` in lower case, and one with `RETRY-AFTER` in upper case
- a 429 whose `Retry-After` is an HTTP-date: once in the future, once in the past
- a 429 that only has `X-RateLimit-Reset`, and that reset is already behind `now`
- a 429 that has both `Retry-After` and a reset — `Retry-After` wins
- a 200 with rate-limit headers, and a 200 whose `X-RateLimit-Remaining` is `0`
- a duplicate `X-RateLimit-Limit` (never output) and a duplicate `X-RateLimit-Remaining`
  where the last value decides the verdict
- an `X-RateLimit-Remaining` of `n/a`
- a block with no status line at all, and blank lines inside a block

## Timebox

4 minutes. In python, `email.utils.parsedate_to_datetime` does the date; in awk there is
no date library at all, so convert the civil date to epoch days by hand and multiply.
