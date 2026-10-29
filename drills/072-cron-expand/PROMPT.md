# 072-cron-expand

> "Five crontab lines, and I want to see the actual schedule without running anything.
> Expand every field to the values it really means."

## Task

`in/jobs.txt` is tab-separated: a job name, then the five crontab fields
(`minute hour day-of-month month day-of-week`). Whitespace between fields is free-form.

## Rules

1. Skip blank lines and lines beginning with `#`.
2. Job names match `[a-z0-9_-]+`.
3. Field bounds: minute 0-59, hour 0-23, day-of-month 1-31, month 1-12, day-of-week 0-6
   with `7` accepted as Sunday.
4. A field is a comma list of items. Each item is `*`, a single value, `a-b`, or either one
   with a `/step` suffix (`*/15`, `5-25/10`). Steps are positive integers.
5. Month names `JAN`..`DEC` and weekday names `SUN`..`SAT` may stand in for numbers,
   case-insensitively, anywhere a number may.
6. Report each field's values ascending, deduplicated, with Sunday as `0`.
7. Any bad field prints `<job>: bad <field> field: <text>` on stderr and exits non-zero.
8. Do not read the system crontab or call `crontab(1)`.

## Output

- `out/schedule.json` - one object: job name to `{"minute": [...], "hour": [...],
  "dom": [...], "month": [...], "dow": [...]}`, each a sorted integer array.
- `out/summary.json` - exactly two integers: `jobs`, and `slots` (the sum over jobs of
  `len(minute) * len(hour)`).

## Messes to expect

- `*/15` and `9-17` in the same line
- `MON-FRI` as a range, `JAN,JUL` as a list
- `7` for Sunday
- a step over a range, `5-25/10`

## Timebox

4 minutes. Expand each field independently into a set, then sort it.
