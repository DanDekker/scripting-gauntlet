# 090-tls-cert-expiry

> "Audit a concatenated bundle of x509 PEM certificates against a fixed audit date
> and list of target hostnames. Identify expired certs, certs expiring within 30 days,
> and check hostname coverage."

## Inputs

1. **`in/bundle.pem`** — one or more PEM certificates concatenated together.
2. **`in/targets.txt`** — list of domain hostnames to check coverage for (one per line, whitespace-stripped).
3. **`in/audit_time.txt`** — reference timestamp in ISO-8601 UTC format (e.g. `2026-10-29T12:00:00Z`).

## Rules

1. Parse each PEM certificate block (`-----BEGIN CERTIFICATE-----` to `-----END CERTIFICATE-----`).
2. Extract:
   - `not_after`: expiration timestamp (ISO 8601 `YYYY-MM-DDTHH:MM:SSZ`)
   - `subject_cn`: Common Name from Subject
   - `sans`: list of Subject Alternative Name DNS names (lowercase)
3. Status evaluation relative to `audit_time`:
   - `expired`: if `not_after <= audit_time`
   - `warning`: if `not_after > audit_time` and `not_after <= audit_time + 30 days` (inclusive of 30*86400 seconds)
   - `ok`: otherwise
4. Target coverage check:
   A target hostname matches a certificate if any of its SAN DNS entries or subject CN match:
   - exact case-insensitive match (e.g., `api.example.com` matches `api.example.com`)
   - single-level wildcard match (e.g., `*.example.com` matches `api.example.com`, but does NOT match `sub.api.example.com` or bare `example.com`)
   Target is covered if at least one certificate with status `ok` or `warning` covers it. If only `expired` covers it or no cert covers it, target is `uncovered`.

## Outputs

1. **`out/certs.csv`** — header `cn,not_after,status`. Sorted by `not_after` ascending, then `cn` ascending.
2. **`out/coverage.json`** — object with keys:
   - `audit_time`: ISO string matching input
   - `total_certs`: integer
   - `expired_count`: integer
   - `warning_count`: integer
   - `ok_count`: integer
   - `uncovered_targets`: list of target domain strings from `targets.txt` that are not covered by any valid/warning cert (in original input order)
