# 049-pid-tree

> "Same ps capture. Draw me the family tree — depth of every process, everything living
> under the Safari pid 205, and whatever got orphaned when its parent died."

## Task

`in/ps-snapshot.txt` is a captured `ps -axo pid,ppid,rss,%cpu,command` table (same shape
as 048).

## Rules

1. The first line is the header — skip it, and skip blank lines.
2. `depth` is 0 when a process's `ppid` is **not a pid in the table** (that includes
   `ppid` 0). Otherwise `depth(child) = depth(parent) + 1`.
3. An **orphan** is a process whose `ppid` is not 0 and is not a pid in the table.
4. `command` is everything after the fourth whitespace field, whitespace runs collapsed
   to one space.
5. `descendants` of a pid are all of its children, its children's children, and so on —
   transitively. The starting pid itself is not a descendant.

## Output

**`out/tree.csv`** — header exactly `pid,ppid,depth,command`, one row per process, sorted
by `depth` ascending, ties by `pid` ascending (numeric).

**`out/descendants.txt`** — the pids under **205**, one per line, ascending numeric, no
header.

**`out/orphans.csv`** — header exactly `pid,ppid,command`, one row per orphan, sorted by
`pid` ascending (numeric).

**`out/summary.json`** — exactly three keys: `processes`, `roots` (processes at depth 0),
`max_depth`.

No field may be quoted; nothing in this capture contains a comma.

## Messes to expect

- two pids whose `ppid` points outside the table (`499` and `2`)
- a blank line, and a `<defunct>` zombie that still has a parent
- a four-deep chain: 205 → 206 → 208 → 209
- repeated command lines that differ only in arguments

## Timebox

3 minutes. Read the table into arrays, memoize a recursive `depth()`, walk children with a
queue for the descendants.
