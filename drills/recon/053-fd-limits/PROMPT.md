# 053-fd-limits

> "The hud service keeps dying with EMFILE and the box won't give me live /proc. Here's
> the fd listing I captured and the limits line for it — who is at or over their limit?"

## Task

`in/fd-listing.txt` is a captured listing of open descriptors across several processes;
`in/fd-limit.txt` is the captured `Max open files` line for those processes.

## Rules

1. A listing row is `pid`, `fd number`, `target`, whitespace-separated. Skip any line
   whose first field is **not all digits** (this capture starts with a `PID FD TARGET`
   header) and skip blank lines.
2. One row is one open descriptor. Descriptors are counted per pid — two rows pointing at
   the same file are two descriptors.
3. In `fd-limit.txt`, `#` starts a comment line. The limit is the **first integer** on the
   first line that is not a comment.

## Output

**`out/fd-counts.csv`** — header exactly `pid,descriptors`, one row per pid, sorted
`descriptors` **descending**, ties by `pid` **ascending** (numeric).

**`out/flagged.csv`** — header exactly `pid,descriptors,limit`, one row per process with
`descriptors >= limit`, sorted by `pid` **ascending** (numeric). Header only when nobody
is over.

**`out/summary.json`** — exactly four keys: `processes` (distinct pids), `descriptors`
(rows counted), `limit`, `flagged` (rows in `flagged.csv`).

## Messes to expect

- a header line, a blank line, and ragged spacing
- a process sitting exactly **on** the limit — that one is flagged
- many rows sharing a target (`socket:[...]`), so counting targets instead of rows lies
- the limit file is a `/proc` limits row, not a bare number

## Timebox

3 minutes. `awk` into a `pid -> count` map, then two sorts and one comparison.
