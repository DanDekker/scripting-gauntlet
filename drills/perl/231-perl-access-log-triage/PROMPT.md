# 231-perl-access-log-triage

> "Our daily traffic rollup started reporting fewer requests than actual log lines,
> and crashed under warnings with `Argument '-' isn't numeric in addition`. The parser
> assumed every request sends a body, dropping 304 and 401 records."

## Input

`in/access.log` — web server log lines in Combined Log Format:

```text
192.168.1.10 - frank [30/Oct/2026:10:00:01 +0000] "GET /api/v1/health HTTP/1.1" 200 42 "-" "curl/7.88.1"
192.168.1.20 - - [30/Oct/2026:10:00:02 +0000] "POST /api/v1/login HTTP/1.1" 401 - "-" "python-requests/2.31"
192.168.1.10 - frank [30/Oct/2026:10:00:03 +0000] "GET /assets/app.js HTTP/1.1" 304 - "https://app.example.com" "Mozilla/5.0"
10.0.0.5 - - [30/Oct/2026:10:00:04 +0000] "GET /api/v1/data HTTP/1.1" 500 128 "-" "Go-http-client/1.1"
192.168.1.10 - - [30/Oct/2026:10:00:05 +0000] "GET /bad HTTP/1.1" 404 15 "-" "curl/7.88.1"
10.0.0.5 - - [30/Oct/2026:10:00:06 +0000] "POST /api/v1/data HTTP/1.1" 201 512 "-" "Go-http-client/1.1"
192.168.1.20 - - [30/Oct/2026:10:00:07 +0000] "GET /api/v1/health HTTP/1.1" 200 42 "-" "curl/7.88.1"
10.0.0.5 - - [30/Oct/2026:10:00:08 +0000] "GET /robots.txt HTTP/1.1" 200 24 "-" "Googlebot/2.1"
```

Empty lines and lines starting with `#` are ignored.

## Rules

1. Parse each valid log line from `in/access.log`:
   - Extract the client IP (first field).
   - Extract the HTTP status code (3-digit integer).
   - Extract the body bytes sent: an integer or `-`.
     If `-`, the request sent 0 body bytes.
2. Group status codes into families:
   - Status 200–299: `s2xx`
   - Status 300–399: `s3xx`
   - Status 400–499: `s4xx`
   - Status 500–599: `s5xx`
3. Aggregate metrics by client IP:
   - Total number of requests.
   - Total body bytes sent.
4. **`out/clients.csv`** — header `ip,requests,bytes`.
   - One row per unique client IP.
   - Sorted by `requests` **descending**; ties broken by `bytes` **descending**;
     further ties broken by `ip` **ascending** in byte order.
5. **`out/summary.json`** — keys `requests`, `total_bytes`, `s2xx`, `s3xx`, `s4xx`, `s5xx`.
   - `requests` — total number of parsed log lines.
   - `total_bytes` — sum of body bytes across all parsed requests.
   - `s2xx`, `s3xx`, `s4xx`, `s5xx` — count of requests in each status family.
   - Emit as a single compact JSON object.

## Messes to expect

- `bytes` is `-` when no response body was sent (e.g. status 304, 401). Naive numeric
  coercion warns or fails to match regex patterns requiring `\d+`.
- Multi-key sorting: primary sort is numeric descending, secondary is numeric descending,
  tertiary is string ascending.

## Timebox

Five minutes.
