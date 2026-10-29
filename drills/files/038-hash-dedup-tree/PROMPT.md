# 038-hash-dedup-tree

> "This backup tree has the same report in it three times under three names. Before I
> ship it anywhere, tell me what's redundant and how many bytes I'd get back."

## Task

Group every file in `in/tree/` by content hash. Inside a group, one file is the
**keeper**: the one with the **shortest path**, ties broken by the **lexicographically
smallest** path. Every other file in that group is a duplicate.

## Rules

1. Paths are relative to `in/tree/`, forward slashes, e.g. `docs/report.txt`.
2. Hash file **contents** with sha256, lowercase hex. Names and timestamps are irrelevant.
3. A **zero-byte file is never a duplicate**. Skip it entirely: it joins no group, is
   never a keeper, and contributes 0 bytes of waste. It is only counted in `empty`.
4. A group with a single file produces no rows — it has no duplicates.
5. `wasted_bytes` is the sum of `bytes` over every reported row: what you would free by
   deleting the duplicates and keeping the keepers.

## Output

**`out/dupes.csv`** — header `keeper,duplicate,sha256,bytes`, one row per duplicate file,
sorted by `keeper` ascending then `duplicate` ascending (byte order). `keeper` and
`duplicate` are tree-relative paths; `bytes` is the file size (identical across a group).

**`out/summary.json`** — exactly five keys:

- `files` — every regular file under `in/tree/`, zero-byte ones included
- `unique_hashes` — distinct hashes among the **non-empty** files
- `duplicate_files` — how many rows you wrote to `dupes.csv`
- `wasted_bytes` — as defined above
- `empty` — how many zero-byte files you skipped

## Messes to expect

- the same 167 bytes under three different names, one of them nested two levels deep
- a filename with a space and parentheses in it
- a zero-byte placeholder that must not be grouped
- lots of distinct files, so most groups have exactly one member
- a `.bak` file that is byte-identical to the file it backs up

## Timebox

3 minutes. `find -print0` + one hash per file, then an awk group-by-hash.
