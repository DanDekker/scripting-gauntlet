# 232-perl-process-triage

> "Our resource watchdog alert sent truncated command names to the ops channel. It did
> a bare `split /\\s+/` on `ps` output, so `postgres: writer process` became just `postgres:`
> and engineers could not tell which background worker was pegging the CPU."

## Input

- `in/thresholds.ini` — `key = value` alert limits:
  - `cpu_pct` — CPU percentage threshold (float, e.g. `80.0`).
  - `rss_kb` — RSS resident memory threshold in kilobytes (integer, e.g. `1000000`).

```ini
cpu_pct = 80.0
rss_kb = 1000000
```

- `in/processes.txt` — process listing table:
  - Header: `USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND`
  - Columns 1 through 10 are whitespace-separated single tokens.
  - Column 11 (`COMMAND`) is everything from the 11th whitespace boundary to the end of the line,
    preserving internal spaces and flags.

```text
USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
root 1 0.0 0.1 168920 12400 ? Ss Oct28 0:03 /sbin/init splash
www-data 1024 12.5 4.2 892400 345000 ? S 09:15 1:22 /usr/bin/node /app/server.js --port 8080
postgres 1042 85.0 18.0 2450000 1480000 ? Sl 08:30 45:10 postgres: writer process
app 1150 95.2 3.1 520000 256000 ? R 10:00 15:44 /usr/bin/perl /opt/worker/job.pl --queue high
redis 1160 2.1 14.5 1800000 1200000 ? S 08:00 2:10 /usr/bin/redis-server 127.0.0.1:6379
www-data 1180 0.2 1.0 210000 82000 ? S 10:12 0:02 nginx: worker process
backup 1200 82.0 15.0 2100000 1100000 ? R 10:20 5:00 /usr/bin/tar -czf /backup/data.tar.gz /var/data
```

## Rules

1. Read `in/thresholds.ini` for `cpu_pct` and `rss_kb`.
2. Parse `in/processes.txt`, skipping the header line and any blank or commented lines.
3. Classify each process:
   - `cpu` if `%CPU >= cpu_pct` and `RSS < rss_kb`
   - `memory` if `RSS >= rss_kb` and `%CPU < cpu_pct`
   - `both` if `%CPU >= cpu_pct` and `RSS >= rss_kb`
   - Process is ignored if neither condition is met.
4. **`out/runaways.csv`** — header `pid,user,cpu,rss,flag,command`.
   - One row per flagged process (`cpu`, `memory`, or `both`).
   - Sorted by `%CPU` **descending**; ties broken by `RSS` **descending**; ties broken by `PID` **ascending**.
   - `cpu` formatted with one decimal place (e.g. `95.2`, `85.0`).
5. **`out/summary.json`** — keys `total_processes`, `flagged`, `cpu_only`, `mem_only`, `both`.
   - `total_processes` — total valid processes inspected.
   - `flagged` — number of processes written to `out/runaways.csv`.
   - `cpu_only` — processes with flag `cpu`.
   - `mem_only` — processes with flag `memory`.
   - `both` — processes with flag `both`.
   - Emit as a single compact JSON object.

## Messes to expect

- `COMMAND` can contain spaces, flags, and arguments. A naive `split /\\s+/` without a
  limit cuts the command into separate tokens, losing everything after the binary name.
- Floating-point comparisons for CPU percentage vs integer comparison for RSS.

## Timebox

Five minutes.
