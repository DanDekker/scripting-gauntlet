# 198-perl-state-variables

> "An incident monitor processes sequential health check events. It must track consecutive
> failure streaks per service and raise an alert whenever a service suffers 3 consecutive failures.
> A previous implementation used `my %streaks` inside the helper, resetting the counter on every check."

## Input

`in/checks.log` — timestamped health check records `<timestamp> <service> <status>`:

```
10:00:01 api OK
10:00:02 auth FAIL
10:00:03 auth FAIL
10:00:04 api FAIL
10:00:05 auth FAIL
10:00:06 auth OK
10:00:07 api FAIL
10:00:08 api FAIL
10:00:09 auth FAIL
```

Blank lines and `#` comments are skipped. Status is either `OK` or `FAIL`.

## Rules

1. Implement `record_check($service, $status)` using lexical persistent state:
   - Use `state %streaks;` (enabled with `use feature 'state';` or `use v5.10;`).
   - If `status == "FAIL"`: increment streak for `$service` by 1.
   - If `status == "OK"`: reset streak for `$service` to 0.
   - Return current streak and alert flag (`"true"` if streak >= 3, else `"false"`).
2. Process lines in stream order, recording step index starting at 1.

## Output

Write exactly these files to `$OUT`:

1. **`out/streaks.csv`** — header `step,timestamp,service,status,streak,alert`.
2. **`out/summary.json`** — keys `checks`, `alerts`, `max_streak`. One compact JSON object:
   `{"checks":9,"alerts":2,"max_streak":3}`.

## Messes to expect

- Using `my %streaks` re-allocates the hash on every call, capping streaks at 1 and missing all alerts.
- Streaks must be tracked independently per service name.

## Timebox

Four minutes. Enable `use feature 'state';` and declare `state %streaks;`.
