# 202-bash-filename-inventory

> "Our asset inventory script started reporting files that do not exist and missing
> files that do. It walked the tree with `for f in $(find ...)`, so every name with a
> space in it was torn into two separate names."

## Input

`in/tree/` — a directory tree of regular files. Some file names contain **spaces**.
There is also a symlink and an empty directory.

## Rules

1. Walk `in/tree` recursively and list every **regular file**.
   - Directories are not listed.
   - Symlinks are not listed (a symlink is not a regular file).
2. `path` is the file's path relative to `in/tree`, using `/` as the separator and
   no leading `./`.
3. `bytes` is the file size in bytes.
4. Rows are sorted by `path` ascending, compared byte by byte.
5. **`out/manifest.csv`** — header `path,bytes`, one row per regular file.
6. **`out/summary.json`** — keys `files`, `total_bytes`, `spaces`.
   - `files` — number of regular files listed.
   - `total_bytes` — sum of the sizes of those files.
   - `spaces` — number of listed paths that contain a space character.

## Messes to expect

- File names contain spaces. An unquoted `$(find ...)` splits them on the space.
- The tree contains a symlink and an empty directory; neither is a regular file.

## Timebox

Five minutes. `find -print0` with `while IFS= read -r -d ''` walks any name.
