# 200-ps1-regex-groups

> "A PowerShell log parser uses `-match` with named capture groups to ingest service events.
> When it encountered corrupt or heartbeat log lines, it leaked previous transaction IDs and durations
> into subsequent records because PowerShell does not clear `$Matches` on match failure."

## Input

`in/events.log` — sequence of log lines:

```
LOG 2026-10-29T12:00:01 ID=101 status=SUCCESS duration_ms=42
LOG CORRUPT_EVENT_GARBAGE_NO_ID
LOG 2026-10-29T12:00:03 ID=102 status=FAILED duration_ms=120
LOG HEARTBEAT_PING_IGNORED
LOG 2026-10-29T12:00:05 ID=103 status=SUCCESS duration_ms=15
```

Blank lines and `#` comments are skipped.

## Rules

1. Parse each line against the transaction pattern:
   `^LOG (?<stamp>\S+) ID=(?<id>\d+) status=(?<status>\w+) duration_ms=(?<dur>\d+)$`
2. **Defend against stale state**:
   - Check the boolean result of `$line -match $pattern`.
   - If match succeeds: `valid = "true"`, extract `id`, `status`, and integer `duration`.
   - If match fails: `valid = "false"`, `id = ""`, `status = ""`, `duration = ""`.
   - Do not allow values from `$Matches` to leak across lines.
3. Compute `avg_duration`: integer average duration across valid records (e.g. `[int](177 / 3)` = 59).

## Output

Write exactly these files to `$OUT`:

1. **`out/parsed.csv`** — header `step,id,status,duration,valid`, in input order.
2. **`out/summary.json`** — keys `total_lines`, `valid_records`, `corrupt_lines`, `avg_duration`.
   One compact JSON object:
   `{"total_lines":5,"valid_records":3,"corrupt_lines":2,"avg_duration":59}`.

## Messes to expect

- If a script reads `$Matches['id']` without testing `-match`, lines 2 and 4 inherit stale IDs.

## Timebox

Four minutes. Check `if ($line -match $pattern)` before reading `$Matches`.
