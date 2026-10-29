# 076-runaway-files

> "The build box filled up overnight. Before I delete anything I want the five biggest
> real files, the total, and how much of it is junk I can ignore."

## Task

`in/tree/` is a messy directory. `setup.py` builds it: a couple of large files, a hardlink
pair, a symlink to a directory, a dangling symlink, and some build junk.

## Rules

1. Walk `in/tree/` without following symlinks. Symlinks are never counted, not even when
   they point at a regular file, and a loop must not hang the walk.
2. Only regular files count. Count each inode **once**: a second hardlink to an inode is
   not extra bytes, but it is counted in `links_skipped`. The path reported for an inode
   is the smallest of its links in byte order, so the answer does not depend on walk order.
3. Ignore any path with a component named `node_modules`, `.cache` or `__pycache__`. Its
   bytes are neither in `bytes` nor in the top list; they are reported as `ignored_bytes`.
4. Report the five largest counted files, largest first; equal sizes sort by path
   ascending in byte order. `size_mb` is bytes divided by 1048576, two decimals.
5. `path` is relative to `in/tree/` and uses `/` separators.

## Output

- `out/top_files.csv` - header `rank,path,size_mb`, five rows (`rank` 1..5).
- `out/summary.json` - exactly four integers: `files` (distinct inodes counted), `bytes`
  (their total), `ignored_bytes`, `links_skipped`.

## Messes to expect

- a hardlink that would double-count 5 MiB
- `tmp/loop` pointing at `../var`, and `tmp/self` pointing at itself
- `node_modules` and `node_modules/.cache` holding 6 MiB of junk
- a filename with a space in it

## Timebox

5 minutes. `find -type f` never follows links; dedupe by inode; filter components before
summing.
