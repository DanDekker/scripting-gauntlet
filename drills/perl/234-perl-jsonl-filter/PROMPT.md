# 234-perl-jsonl-filter

> "Our backend incident triage tool crashed on a 500MB JSON Lines dump because it slurped
> the whole file into an array. We need a streaming Perl script that aggregates error rates
> and latency per microservice."

## Input

`in/events.jsonl` — newline-delimited JSON objects:
- Keys include `timestamp`, `service`, `level`, `duration_ms`, `status`.
- Some events may include extra keys (e.g. `error`).
- Blank lines are ignored.

```json
{"timestamp":"2026-10-30T10:00:01Z","service":"auth","level":"INFO","duration_ms":12,"status":200}
{"timestamp":"2026-10-30T10:00:02Z","service":"payment","level":"ERROR","duration_ms":250,"status":500,"error":"gateway timeout"}
{"timestamp":"2026-10-30T10:00:03Z","service":"auth","level":"WARN","duration_ms":150,"status":429}
{"timestamp":"2026-10-30T10:00:04Z","service":"catalog","level":"INFO","duration_ms":35,"status":200}
{"timestamp":"2026-10-30T10:00:05Z","service":"payment","level":"INFO","duration_ms":80,"status":200}
{"timestamp":"2026-10-30T10:00:06Z","service":"auth","level":"ERROR","duration_ms":18,"status":401,"error":"invalid credentials"}
{"timestamp":"2026-10-30T10:00:07Z","service":"catalog","level":"ERROR","duration_ms":450,"status":503,"error":"backend unavailable"}
{"timestamp":"2026-10-30T10:00:08Z","service":"payment","level":"ERROR","duration_ms":120,"status":500,"error":"connection reset"}
```

## Rules

1. Read `in/events.jsonl` line by line, decoding each JSON object with `JSON::PP::decode_json`.
2. For each unique `service`, accumulate:
   - `events` — count of total events.
   - `errors` — count of events where `level eq "ERROR"`.
   - `duration_ms` — total accumulated duration across all events.
   - `avg_duration_ms` — average duration in milliseconds (`duration_ms / events`), formatted to 1 decimal place.
3. **`out/services.csv`** — header `service,events,errors,total_duration_ms,avg_duration_ms`.
   - One row per service.
   - Sorted by `errors` **descending**; ties broken by `events` **descending**; further ties broken by `service` **ascending** in byte order.
4. **`out/summary.json`** — keys `total_events`, `total_errors`, `total_duration_ms`, `services_count`.
   - Emit as a single compact JSON object.

## Messes to expect

- Stream processing: decode each line individually rather than slurping the entire file into memory.
- Multi-key sorting: numeric descending for errors and events, alphabetical ascending for service name.

## Timebox

Five minutes.
