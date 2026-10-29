# 132-server-header-audit

> "Before this goes live I need the security headers checked on every response we captured.
> Tell me exactly which header on which URL is wrong and how it is wrong — missing, too
> weak, or just the wrong value. And don't hold a 301 or a 500 against us."

## Input

**`in/responses.txt`** — captured HTTP responses, one block after another:

```
GET / HTTP/1.1
HTTP/1.1 200 OK
Server: nginx/1.24.0
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

## Rules

1. **Blocks.** A block starts at a line that is a request line: `<METHOD> <path> HTTP/1.1`,
   where the method is uppercase letters only. Everything up to the next request line or
   EOF belongs to that block. Blank lines are ignored, and lines before the first request
   line belong to no block.
2. **Status line.** Inside a block, the status line is the **first** line that starts with
   `HTTP/`. It must yield a three-digit code — `HTTP/<version>` then whitespace then three
   digits (`^HTTP/[0-9.]+ +([0-9]{3})`). A block with **no** such line is **skipped** and
   counted once in `skipped`; nothing else in it is read.
3. **Headers.** Only the lines **after** the status line are considered. A header line is
   `Name: value` where the name is letters, digits and hyphens only (so a line whose
   name part contains a space is not a header and is ignored). Names are matched
   **case-insensitively**; values are trimmed. When a header appears more than once in a
   block, the **last** value wins.
4. **Not every response is audited.** A status of `300`–`399` is a **redirect** (result
   `redirect`) and a status of `400`–`599` is an **error** (result `error`); neither is
   checked for headers. Every other status (1xx, 2xx) is **checked**.
5. **The five checks**, in this order, with the canonical header spelling used in the
   output:

   | # | header | passes when | failure reason |
   |---|---|---|---|
   | 1 | `Strict-Transport-Security` | it contains `max-age=` (case-insensitive, no space around `=`); the value between `=` and the next `;` or end, trimmed, is all digits and **greater than 0** | `weak` (present but `max-age` is 0, non-numeric or absent from the value) |
   | 2 | `Content-Security-Policy` | it does **not** contain `*` | `weak` (it contains `*`) |
   | 3 | `X-Content-Type-Options` | the value is `nosniff`, case-insensitively | `wrong-value` |
   | 4 | `X-Frame-Options` | the value is `DENY` or `SAMEORIGIN`, case-insensitively | `wrong-value` |
   | 5 | `Referrer-Policy` | the value is `no-referrer`, `same-origin`, `strict-origin` or `strict-origin-when-cross-origin`, case-insensitively | `wrong-value` |

   Any of the five that is **absent** fails with reason `missing`. An empty value counts
   as present, and fails as `wrong-value` (or `weak` for headers 1 and 2).
6. **Result.** A checked response whose five headers all pass is `pass`. A checked
   response with one or more failures is `fail`, and every failing header is one row.

## Output

Write exactly these files to `$OUT`.

**`out/findings.csv`** — header exactly `url,status,header,reason`, then one row per
failing header of a checked response: responses in **input order**, and within one
response in the **table order above** (1 → 5). No row for a passing header, a redirect or
an error.

- `url` — the path from the request line, verbatim, query string included
  (`GET /old?ref=1 HTTP/1.1` → `/old?ref=1`).
- `status` — the status code as an integer.
- `header` — the header name in the canonical spelling from the table.
- `reason` — exactly `missing`, `weak` or `wrong-value`.

**`out/summary.json`** — an object with exactly these keys:

| key | meaning |
|---|---|
| `responses` | blocks with a valid status line |
| `skipped` | blocks with no status line |
| `checked` | responses audited for headers (not redirect, not error) |
| `pass` | checked responses with no failing header |
| `fail` | checked responses with at least one failing header |
| `redirect` | responses with status 300–399 |
| `error` | responses with status 400–599 |
| `findings` | total rows in `findings.csv` |

## Messes to expect

- a block with no status line at all — skipped, not scored
- a 200 missing three of the five headers, and a 204 with **no** headers
- a 301 that carries nothing worth checking, and a 500 that carries a `max-age=0` — an
  error response is not audited, so the weak header produces no finding
- `Strict-Transport-Security` sent twice, the `max-age=0` one first and the good one last
- `strict-transport-security` / `x-frame-options` in lower case, `X-Content-Type-Options`
  with trailing spaces, and a `MAx-Age=` directive
- `max-age=abc` — present, and still a failure (`weak`)
- `Content-Security-Policy: default-src *` — present, and still a failure (`weak`)
- a line with a space in the name part (`this line: has spaces in the name`) — ignored

## Timebox

4 minutes. Flush a block when the next request line appears, keep a `lowercase name` →
value map per block, then five ifs in table order.
