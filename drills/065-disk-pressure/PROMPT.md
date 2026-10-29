# 065-disk-pressure

> "I have disk reports from three operating systems. Which mounted volumes have 10%
> free space or less? Put them in one report so I can triage the tightest first."

## Task

Read Linux and macOS `df -Pk` captures plus a Windows `Get-Volume` CSV capture. Count
every volume, but report only those with **10.0% free space or less**.

## Rules

1. On Linux and macOS, `df` reports total and available space in 1K blocks. Multiply
   both by 1024 to produce bytes. Free percent is `available / total * 100`, rounded to
   one decimal place.
2. Linux mount point starts at column 6; macOS mount point starts at column 9. The mount
   point continues through the end of the line and may contain spaces.
3. On Windows, `Get-Volume` CSV sizes are already bytes. Use `DriveLetter` and
   `FileSystemLabel` to name a volume as `C:\ (OS)`.
4. Count all input volume rows in `volumes_seen`. A zero-sized volume is malformed:
   name it on stderr and exit non-zero.
5. Sort low-space rows by `free_pct` ascending, then `platform`, then `volume` ascending
   in byte order.

## Output

**`out/low_space.csv`** — header `platform,volume,total_bytes,free_bytes,free_pct`,
then one row for each volume at or below the threshold.

**`out/summary.json`** — exactly `volumes_seen` and `low_space`, both integers.

## Messes to expect

- Linux and macOS use different numbers of columns before the mount point
- one macOS mount point contains a space
- Unix space values are in 1K blocks; Windows values are bytes
- some volumes have lots of space and should not appear in the low-space report

## Timebox

5 minutes. Parse only the fields the report needs, and keep the platform column so the
report is auditable.
