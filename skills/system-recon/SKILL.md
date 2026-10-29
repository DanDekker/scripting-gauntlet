---
name: system-recon
description: Inspect processes, PIDs, resource usage, file descriptors and disk state on a running machine, then turn the raw output into a ranked, reportable answer. Use when asked what is running, who owns a resource, which process is eating memory or CPU or file descriptors, how a process tree is shaped, whether the disk is full, or to capture a system snapshot for later analysis. Not for building services or monitoring daemons.
license: MIT
metadata:
  family: system-recon
  drills: 048-ps-snapshot, 049-pid-tree, 052-resource-usage, 053-fd-limits
---

# System recon

The job is never "run `ps`". It is "answer a question about the machine and show your
work". The shape is always:

**capture → parse → rank → report**

## Capture first, analyse second

```bash
ps -eo pid,ppid,rss,%cpu,comm > /tmp/ps.txt      # the snapshot you will analyse
```

Capture to a file, then analyse the file. Two reasons: the machine's state changes while
you work, so a snapshot keeps your answer consistent with itself; and a captured file can
be re-analysed, diffed, and unit-tested. Every drill in this pack works on a captured
table for exactly this reason.

If you must collect live, collect once, then treat the output as immutable.

## The commands, and their platform differences

| want | Linux | macOS |
| --- | --- | --- |
| process table | `ps -eo pid,ppid,rss,%cpu,comm` | `ps -axo pid,ppid,rss,%cpu,comm` |
| sockets for a pid | `ls -l /proc/<pid>/fd` | `lsof -p <pid>` |
| disk | `df -k` | `df -k` |
| cpu count | `nproc` | `sysctl -n hw.ncpu` |
| load | `cat /proc/loadavg` | `uptime` |

`/proc` is Linux-only. `ps` is everywhere but its **column order and options differ** —
always pass an explicit format string, never rely on the default columns.

## Parsing a process table

```bash
# top 5 by RSS, tie-break by pid ascending
awk 'NR>1 && $3 ~ /^[0-9]+$/ { printf "%d\t%s\t%d\n", $3, $1, $2 }' ps.txt \
  | sort -t$'\t' -k1,1nr -k2,2n | head -5
```

Things that will bite you:

- **Kernel threads** show as `[kworker/0:1]` — the whole bracketed token is the name, and
  an internal `/` means you cannot split the name on `/`.
- **`%CPU` in `ps` is a lifetime average**, not instantaneous. `top` gives instantaneous.
- **RSS is resident, VSZ is virtual.** A process can have a huge VSZ and a small RSS;
  most "who is eating memory" answers want RSS.
- **Command names get truncated** in `ps aux` output. `comm` is the full name.
- **PID reuse** means a PID in an old capture may be a different process now.

## Building the tree

The parent is the `PPID` column. Depth is the length of the chain up to a root.

```awk
{ parent[$1] = $2 }
# a pid whose ppid is not in the table is an orphan (reparented to init, or stale)
```

Orphans are normal (pid 1 reaps them) — report them, do not treat them as errors.

## File descriptors

```bash
ls /proc/<pid>/fd | wc -l        # Linux
lsof -p <pid> | wc -l            # portable-ish
```

Compare the count against the limit (`ulimit -n`, or the `Max open files` line in
`/proc/<pid>/limits`). "At or over" the limit is the interesting state — the next open
fails. Flag `>=`, not `>`.

## Disks

`df -k` gives 1K blocks. Used% is `(used / (used + available)) * 100` — **not**
`used / total`, because `avail` excludes the reserved blocks, and the two disagree on
filesystems with reserved space. When mapping a path to its filesystem, match the **longest
mount point**, and match on a `/` boundary: `/var/lib/appdata` must not capture
`/var/lib/app/queue.db`.

## Reporting

Lead with the answer, then the evidence table, then the caveat you know about
("RSS not VSZ", "captured at 10:04"). A recon report that does not say when it was taken
is not a recon report.

Prove it against `drills/recon/048-ps-snapshot`, `049-pid-tree`, `052-resource-usage`,
`053-fd-limits`.
