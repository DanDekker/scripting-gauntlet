# 052-resource-usage

> "The queue file at /var/lib/app/queue.db is on its own volume and I can't shell into the
> box. I've got a saved `df -k`, the `uptime` line and `hw.ncpu`. Is the volume filling up,
> and is the machine actually loaded?"

## Task

Three captured files: `in/df-k.txt`, `in/uptime.txt`, `in/cpucount.txt`.

## Rules

1. `df -k` row: `device`, `1K-blocks`, `used`, `available`, `Use%`, then the **mount
   point is the rest of the line** (fields 6..NF — one mount point here contains a space).
   Strip the `%` from `Use%`. Skip the header line.
2. The data path is `/var/lib/app/queue.db`. The filesystem that contains it is the one
   with the **longest** mount point that either equals the path or is followed by a `/` in
   the path. `/var/lib/appdata` does **not** contain it; `/var/lib/app` does.
3. `uptime.txt` holds one `uptime` line — the **1-minute** load is the first number after
   `load averages:`.
4. `cpucount.txt` holds one integer: the CPU count.

## Output

**`out/resources.json`** — exactly these keys:

- `path` — the data path, unchanged
- `mount` — the mount point that contains it
- `used_pct` — that filesystem's `Use%`, integer
- `available_kb` — that filesystem's `Available`, integer
- `load1` — the 1-minute load average, number
- `cpus` — integer
- `load_per_cpu` — `load1 / cpus`, rounded to two decimals
- `warning` — `true` when `used_pct >= 90`, else `false`
- `mounts` — number of `df` rows parsed

If no filesystem contains the path, print the path on stderr and exit non-zero.

## Messes to expect

- `/var`, `/var/lib` and `/var/lib/app` all prefix the path — only the longest wins
- a sibling mount `/var/lib/appdata` that a naive `startswith` picks up
- a mount point with a space in it (`/Volumes/Backup Disk`)
- `Use%` carries a `%`, and one filesystem is at 97% while ours is at 61%

## Timebox

3 minutes. `df` into an awk array of mount/pct/avail, then one longest-prefix scan.
