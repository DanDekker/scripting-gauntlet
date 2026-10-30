# 201-bash-log-rotate

> "Our nightly log rotation script stopped compressing anything and left old files
> behind for a month. It computed each log's age by subtracting day numbers, so any
> log from a previous month came out with the wrong age — and the ones we needed to
> delete were kept for another month."

## Input

- `in/policy.txt` — `key=value` lines:

```text
today=2026-10-29
compress_after_days=7
delete_after_days=30
```

- `in/logs/` — log files named `svc-YYYY-MM-DD.log`, plus files that do not follow
  that naming convention.

## Rules

1. Read `in/policy.txt` for `today`, `compress_after_days` and `delete_after_days`.
2. For every regular file directly inside `in/logs/` (no recursion):
   - If the name does **not** match `svc-YYYY-MM-DD.log` exactly, **ignore** it: do
     not copy it, do not list it in the report, and count it as `ignored`.
   - Otherwise parse the date and compute `age_days` = the number of days from the
     log's date to `today` (`today` minus the log date). A log dated after `today`
     has a **negative** age.
   - `age_days >= delete_after_days` → action `delete`
   - otherwise `age_days >= compress_after_days` → action `compress`
   - otherwise → action `keep`
3. Build `$OUT/logs/` as the rotated log directory:
   - `keep` → copy the original file unchanged to `$OUT/logs/<name>`
   - `compress` → write gzip-compressed content to `$OUT/logs/<name>.gz`; the
     decompressed bytes must equal the original file exactly
   - `delete` → the file does **not** appear in `$OUT/logs/`
   - ignored files do **not** appear in `$OUT/logs/`
4. **`out/rotation.csv`** — header `file,age_days,action`. One row per named log
   (`svc-*.log`), sorted by file name ascending. `file` is the base name, `age_days`
   is an integer, `action` is `keep`, `compress` or `delete`.
5. **`out/summary.json`** — keys `kept`, `compressed`, `deleted`, `ignored`. One
   compact JSON object.

## Messes to expect

- The fixture dates straddle month and year boundaries. Subtracting the day numbers
  alone turns a 242-day-old log into a 28-day-old one.
- One log is dated after `today`.
- `in/logs/` contains a file whose name does not follow the convention.

## Timebox

Five minutes. Compute the age with a real day count, not field subtraction.
