# 233-perl-cron-schedule

> "Our server maintenance window kicked off early and ran into automated cron jobs.
> The operator scanned `/etc/crontab` by eye and missed a `*/15` recurring sweep and a
> weekday range job, terminating workers mid-sync."

## Input

- `in/target.ini` — `key = value` target execution window:
  - `minute` — target minute (0–59)
  - `hour` — target hour (0–23)
  - `dom` — target day of month (1–31)
  - `month` — target month (1–12)
  - `dow` — target day of week (0–7, where 0 and 7 are Sunday, 1 is Monday, ..., 5 is Friday)

```ini
minute = 45
hour = 14
dom = 30
month = 10
dow = 5
```

- `in/crontab.txt` — crontab format file:
  - Lines starting with `#` and blank lines are ignored.
  - Active lines have 6 whitespace-separated parts: `min hour dom mon dow command`.
  - `command` is everything after the 5th whitespace boundary, preserving arguments and flags.

```text
# System crontab for background workers
# min hour dom mon dow command
*/15 * * * * /opt/scripts/healthcheck.sh --quick
0 2 * * * /opt/scripts/backup.pl --full
30 4 1 * * /opt/scripts/monthly-report.sh
0 14 * * 1-5 /opt/scripts/sync-ldap.pl --dry-run=0
45 14 * * * /opt/scripts/midday-sweep.sh
0 14 30 10 * /opt/scripts/october-audit.sh
45 14 * 12 * /opt/scripts/december-only.sh
45 14 * * 0,6 /opt/scripts/weekend-sweep.sh
45 14 1-15 * * /opt/scripts/early-month.sh
45 14 20-31 10 1-5 /opt/scripts/late-october-weekday.sh
0 16 * * * /opt/scripts/teatime-ping.sh
```

## Rules

1. Read `in/target.ini` for the target timestamp values.
2. Read `in/crontab.txt`, skipping comments and empty lines.
3. For each active cron entry, determine whether it matches the target window across all 5 schedule fields:
   - `*` matches any value.
   - `*/N` matches if `target_val % N == 0`.
   - `A-B` matches if `A <= target_val <= B`.
   - `A,B,C` matches if `target_val` equals any item in the comma-separated list.
   - Explicit number `N` matches if `target_val == N`.
4. **`out/matched.txt`** — list of matched commands, one per line in crontab order.
5. **`out/summary.json`** — keys `total_entries`, `matched`. One compact JSON object:
   - `total_entries` — total active cron lines evaluated.
   - `matched` — number of commands written to `out/matched.txt`.

## Messes to expect

- The command field can contain spaces, paths, and flags. `split /\s+/, $line, 6` ensures the command is preserved intact.
- Range expressions (`20-31`), lists (`0,6`), and step expressions (`*/15`).

## Timebox

Five minutes.
