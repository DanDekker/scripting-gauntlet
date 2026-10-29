# 077-open-deleted

> "df says the disk is full but du says it is not. Something deleted a big file while a
> process kept writing to it. Tell me who is holding the space and how much."

## Task

`in/lsof.txt` is an `lsof +L1` capture, header included. Each data row has the columns
`COMMAND PID USER FD TYPE DEVICE SIZE/OFF NLINK NODE NAME`; `NAME` is field 10 and may
contain spaces.

## Rules

1. Skip the header line (its first field is `COMMAND`), blank lines, and rows with fewer
   than 10 fields.
2. Only rows that hold a deleted file count: `TYPE == REG`, `FD` matches `[0-9]+[rwu]?`,
   `NLINK == 0`, and `NAME` ends with exactly ` (deleted)`.
3. `SIZE/OFF` is the number of bytes held; it must be a non-negative integer.
4. Group by `PID`. `command` is that process's `COMMAND`; `files` counts its rows.
5. Sort by total bytes descending, then `pid` ascending. `bytes_mb` is bytes divided by
   1048576, two decimals.

## Output

- `out/deleted.csv` - header `pid,command,bytes_mb,files`, one row per holding process.
- `out/summary.json` - exactly four values: `processes`, `files`, `reclaimable_mb` (two
  decimals) and `top_pid` (the pid holding the most bytes; ties go to the smaller pid).

## Messes to expect

- `cwd` and `DIR` rows pointing at deleted directories
- a deleted character device, which holds no ordinary data
- an ordinary open file that is **not** deleted
- paths with spaces before the ` (deleted)` marker

## Timebox

3 minutes. The ` (deleted)` suffix is the only reliable marker; the TYPE and NLINK checks
keep the accounting honest.
