# 062-http-retries

> "This endpoint is flaky during warm-up. Tell me which probes eventually worked,
> which failed for good, and how many requests you actually made."

## Task

Read endpoint names from `in/endpoints.txt`. For each name, GET `$API_BASE/<name>` in
input order. The local mock server returns JSON. For a `200` response, the JSON has
an `items` array; report its length.

## Rules

1. Skip blank and `#` comment lines. Endpoint names contain lowercase letters only.
2. A `503` is temporary. Retry it up to **three total requests** for that endpoint.
   Do not retry any other HTTP status. Do not sleep between attempts.
3. Curl transport failures (no HTTP response) are a broken probe: print the endpoint
   on stderr and exit non-zero. An HTTP `404` is a reported endpoint failure, so keep
   probing the remaining names.
4. Parse the body only on `200`. If its JSON is invalid or `items` is not an array,
   print the endpoint and exit non-zero.

## Output

- `out/results.csv`: header `endpoint,status,attempts,http_code,items`, one row per
  endpoint in input order. `status` is `ok` for `200`, otherwise `failed`. `http_code`
  is the final HTTP code. `items` is an integer on success and an empty cell on failure.
- `out/summary.json`: exactly four integers: `endpoints`, `ok`, `failed`, `requests`.

## Messes to expect

- blank and comment lines in the endpoint list
- one endpoint that needs two retries before succeeding
- a `404` with a JSON error body that must not be parsed as an item response

## Timebox

4 minutes. Capture curl's HTTP code separately from its process exit status.
