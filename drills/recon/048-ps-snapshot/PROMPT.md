# 048-ps-snapshot

> "The box is swapping and I can't run ps on it. I saved a `ps` table before it got bad —
> give me the five fattest processes by RSS, and tell me who's running the most copies of
> themselves."

## Task

`in/ps-snapshot.txt` is a captured `ps -axo pid,ppid,rss,%cpu,command` table.

## Rules

1. The first line is the header (`PID PPID RSS %CPU COMMAND`) — skip it, and skip blank
   lines. Every other line is a process.
2. Fields are **whitespace-separated**: `pid`, `ppid`, `rss` (KB), `cpu`, then the command
   line is **everything after the fourth field**, with runs of whitespace collapsed to one
   space.
3. `rss_kb` is an integer, `cpu` is the `%CPU` value printed with one decimal.
4. For the per-command count, `command` is the **executable name**: take the first token
   of the command line. If that token starts with `[` it is a kernel thread and the whole
   token is the name (`[kworker/0:1]` stays as-is — the slash is part of the name, not a
   path). Otherwise take its basename: `/usr/bin/sshd -D` counts as `sshd`, and a bare
   `bash /opt/run.sh` counts as `bash`.

## Output

**`out/top_rss.csv`** — header exactly `pid,ppid,rss_kb,cpu,command`, then the **5**
processes with the largest `rss_kb`, sorted `rss_kb` **descending**, ties by `pid`
**ascending** (numeric).

**`out/commands.csv`** — header exactly `command,processes`, one row per distinct
executable: sorted `processes` **descending**, ties by `command` **ascending** (byte
order, `LC_ALL=C`).

**`out/summary.json`** — exactly three keys: `processes` (data lines parsed),
`total_rss_kb` (sum of every `rss_kb`), `commands` (distinct executables).

No field may be quoted; nothing in this capture contains a comma.

## Messes to expect

- a blank line in the middle of the table, and ragged column widths
- a zombie: `node <defunct>` with `rss` 0
- bracketed kernel threads such as `[kworker/0:1]`
- two Safari processes on the same path, and a three-way tie on `15320` KB

## Timebox

3 minutes. One `awk` to normalize the table into a temp file, then `sort` twice.
