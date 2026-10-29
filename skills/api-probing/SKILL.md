---
name: api-probing
description: Probe an HTTP API before trusting it — check health, follow pagination links, time requests, handle auth safely, and prove what was returned. Use when asked whether a service is up, what shape its responses have, whether pagination terminates, how fast an endpoint is, or to pull a complete dataset from a paginated endpoint. Not for designing or deploying APIs.
license: MIT
metadata:
  family: api-probing
  drill: 003-http-probe
---

# API probing

You are a visitor, not the owner. The job is to find out what is true, then say so.

## Order of operations

1. **Health first.** Never build on a service that says it is unhealthy.

```bash
curl -fsS "$API_BASE/health" | jq .
```

Check the *body*, not just the exit code: `200` with `{"ok": false}` is a down service.

2. **Probe the shape before writing a parser.**

```bash
curl -fsS "$API_BASE/api/v1/items?page=1" | jq 'keys'
curl -fsS "$API_BASE/api/v1/items?page=1" | jq '.items[0]'
```

Two seconds now saves twenty minutes of parsing the wrong field.

3. **Page by following `next`**, not by counting. A `next` that is a relative path
   (`/api/v1/items?page=2`) is normal — concatenate onto the base, don't reconstruct.

```bash
next="/api/v1/items?page=1"
while [ -n "$next" ] && [ "$next" != "null" ]; do
  body=$(curl -fsS "$API_BASE$next")
  printf '%s' "$body" | jq -c '.items[]'
  next=$(printf '%s' "$body" | jq -r '.next // empty')
done
```

4. **Cap the loop and detect repeats.** A pagination bug in *their* code must not hang
   *your* job. 50 pages plus a visited-set is three lines and saves an afternoon.

## Retry, without a framework

```bash
for attempt in 1 2 3; do
  curl -fsS "$URL" && break
  sleep "$attempt"
done
```

That is the whole budget. Backoff with jitter, circuit breakers, and retry middleware
belong to services, not to a probe.

## Auth, without leaking

Pass tokens in an environment variable or a header file — never as a command-line
argument, where `ps` exposes them to every user on the box.

```bash
curl -fsS -H "Authorization: Bearer $TOKEN" "$URL"     # good
curl -fsS "$URL?token=$TOKEN"                            # lands in logs and history
```

## Timing

One number, from curl itself, no benchmarking harness:

```bash
curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' "$URL"
```

## Traps

- **`200` with an error body.** Always validate a field (`jq -e '.ok == true'`).
- **`next` that never becomes null.** Cap and dedupe visited URLs.
- **Rate limits returning `200` and an empty list.** Compare item counts across pages.
- **Timestamps without a timezone.** Assume UTC only after you have checked.
- **`null` vs missing.** `jq '.items // []'` distinguishes "empty" from "absent" only if
  you decide what each means.
- **Retrying non-idempotent writes.** Only retry `GET`/`HEAD`/`PUT`/`DELETE` blindly.

## Reporting

State what you observed: status, version, how many records, how many pages, elapsed time.
"12 items over 3 pages, 204 ms" is proof. "The API works" is not.

Prove it against `drills/003-http-probe` (local mock, no network required).
