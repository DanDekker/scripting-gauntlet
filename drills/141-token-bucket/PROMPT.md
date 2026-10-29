# 141-token-bucket

> "We rate-limit our LLM gateway with two buckets — requests per minute and tokens per
> minute. Here is yesterday's request log and the config we ran. Tell me which requests
> got through, what each bucket had left afterwards, and how many tokens we refused."

## Input

`in/requests.csv` — header `id,timestamp,tokens`.

- `id` — request id (string)
- `timestamp` — integer seconds (not necessarily sorted, repeats are normal)
- `tokens` — integer token count the request asks for

`in/config.json` — one object:

```json
{"rpm_capacity": 5, "rpm_refill_per_sec": 1.0, "tpm_capacity": 1000, "tpm_refill_per_sec": 100.0}
```

## Rules

### Which requests count

A line is a **valid request** only when, after trimming surrounding whitespace, it has
exactly three comma-separated cells, the `id` cell is non-empty, **both** `timestamp` and
`tokens` match `-?[0-9]+`, and `tokens` is not negative.

Everything else — blank and whitespace-only lines, lines with fewer or more than three
cells, a non-integer `tokens` such as `12.5` or `abc`, a negative `tokens` — is skipped and
counted nowhere.

### Order

Process valid requests sorted by `timestamp` ascending, ties broken by **line order in the
input file** (the earlier line first). Ids are not a tie-break.

### The two buckets

Two buckets, both starting **full** at their capacity for the first valid request:

- Request bucket: capacity `rpm_capacity`, refills `rpm_refill_per_sec` per second.
- Token bucket: capacity `tpm_capacity`, refills `tpm_refill_per_sec` per second.

For each valid request at timestamp `t`, in this order:

1. `dt = t - prev_t`, where `prev_t` is the previous request's timestamp; for the first
   request `dt = 0`.
2. Refill: `req_tokens = min(rpm_capacity, req_tokens + dt * rpm_refill_per_sec)` and
   `tok_tokens = min(tpm_capacity, tok_tokens + dt * tpm_refill_per_sec)`.
3. The request costs `1.0` request token **and** `tokens` token-bucket tokens.
   - If `req_tokens >= 1.0` **and** `tok_tokens >= tokens`: `status = accept`; subtract
     `1.0` from the request bucket and `tokens` from the token bucket.
   - Otherwise: `status = reject`; nothing is subtracted.
4. `prev_t = t` — the clock advances and the refill happens for rejected requests too.

A request for `0` tokens still costs its `1.0` request token.

## Output

Write exactly these files to `$OUT`:

1. **`out/decisions.csv`** — header `id,timestamp,tokens,status,req_left,tok_left`. One row
   per valid request, in processing order (the sort above). `status` is `accept` or
   `reject`. `req_left` and `tok_left` are the bucket levels **after** the decision,
   formatted with exactly two decimals (`4.00`, `100.00`).
2. **`out/summary.json`** — object with exactly these keys:
   - `total_requests` — valid requests processed (int)
   - `accepted` — count of `accept` (int)
   - `rejected` — count of `reject` (int)
   - `tokens_served` — sum of `tokens` over accepted requests (int)
   - `tokens_rejected` — sum of `tokens` over rejected requests (int)

## Messes to expect

- `r9, 9, 300` — padding spaces around the cells are not a new field
- `r10,1,12.5` and `r11,6,abc` are not requests at all, and neither is `r14,10`
- `r6,1,-50` has a negative token count, so it is skipped, not rejected
- the file is not chronological: `r1` and `r3` share `t=0`, `r2` and `r8` share `t=3`
- `r7` is rejected because the token bucket is short, so its `req_left` still shows the
  refilled value — a rejection spends nothing
- `r12` asks for 0 tokens and is still accepted (it spends 1 request token)

## Timebox

About five minutes. If you are past that, the approach is wrong.
