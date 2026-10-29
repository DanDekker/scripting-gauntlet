# 041-find-largest

> "Which file under that log dump is the fattest? Disk is full and I need to know what
> to move first."

## Task

`in/` is a small tree with nested directories. Size every regular file in it.

## Rules

1. Consider **regular files only**, at any depth. Directories are not files and never
   appear in the output.
2. Size is the file's **byte size** on disk — not its line count, not its size after
   decoding.
3. Paths in the output are relative to `in/`, with `/` separators, e.g.
   `logs/app/2026-09-30.log`. A file directly in `in/` is just `notes.txt`.
4. Sort by `bytes` **descending**; break ties by `path` **ascending** (byte order).
   The tie-break is part of the contract — two files in this tree have the same size.
5. An empty file is a file: it appears with `0` bytes.

## Output

**`out/sizes.csv`** — header exactly `path,bytes`, then every file, sorted as in rule 4.

**`out/largest.json`** — exactly three keys:

- `files` — how many regular files were found (an integer);
- `bytes` — the total of all their sizes (an integer);
- `largest` — the relative path of the first row of `sizes.csv`.

## Messes to expect

- nested directories two levels deep
- a filename with a space in it (`reports/q3 draft.md`)
- a filename with no extension (`README`)
- two files with byte-identical size

## Timebox

90 seconds. `find ... -type f` plus `wc -c` per file, then one `sort -k2,2nr -k1,1`.
