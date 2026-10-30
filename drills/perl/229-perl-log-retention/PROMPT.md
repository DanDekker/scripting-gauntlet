# 229-perl-log-retention

> "Our nightly log cleaner stopped archiving old files and started deleting recent logs.
> It parsed the date from the filename and passed month 10 to the date converter without
> the 0-based offset — so October became November and every log's age was computed off by a month."

## Input

- `in/policy.ini` — `key = value` settings:
  - `today` — the current reference date (`YYYY-MM-DD`).
  - `compress_days` — minimum age in days to compress an uncompressed log.
  - `delete_days` — minimum age in days to delete a log.

```ini
today = 2026-10-30
compress_days = 3
delete_days = 14
```

- `in/logs/` — directory containing files:
  - Daily access and error logs named `service-YYYY-MM-DD.log` or `service-YYYY-MM-DD.log.gz`.
  - Temporary files ending in `.tmp`.
  - Unrelated files (e.g. `README.txt`).

## Rules

1. Read `in/policy.ini` for `today`, `compress_days`, and `delete_days`.
2. Inspect every regular file directly inside `in/logs/` (no subdirectories):
   - If the filename ends in `.tmp`: action is `delete`, and `age_days` is empty.
   - If the filename matches `^[a-z]+-(\d{4}-\d{2}-\d{2})\.log(?:\.gz)?$`:
     - Calculate `age_days` as the whole number of days between `today` and the log date:
       `today` minus the log date.
     - If `age_days >= delete_days`: action is `delete`.
     - Else if `age_days >= compress_days` and the file does **not** end in `.gz`:
       action is `compress`.
     - Else: action is `keep`.
   - Any other file (not ending in `.tmp` and not matching the log pattern):
     action is `ignore`, and `age_days` is empty.
3. **`out/retention.csv`** — header `file,age_days,action`.
   - One row per file found in `in/logs/`.
   - Sorted by `file` ascending in byte order.
   - `age_days` is an integer for matched logs, or empty for `.tmp` and ignored files.
4. **`out/summary.json`** — keys `files`, `keep`, `compress`, `delete`, `ignore`. One compact JSON object.

## Messes to expect

- `Time::Local::timegm` expects the month argument to be **0..11**, not 1..12.
  Passing month 10 means November (offset 10), throwing the calculation off.
- `opendir`/`readdir` returns `.` and `..`, which are directories and must not be listed.
- Some logs are already compressed (`.gz`). A 10-day-old `.log.gz` is kept, not compressed again.

## Timebox

Five minutes.
