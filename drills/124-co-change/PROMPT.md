# 124-co-change

> "Two files in this repo always break in the same pull request, and nobody can tell me
> which ones. I dumped the commit log with `--name-only` — read it and give me the pairs
> that keep changing together, strongest first."

## Input

`in/log.txt` — a `git log --name-only` style dump, one **block** per commit:

```
commit 4a1b2c3 (HEAD -> main)
src/users.py
src/export.py

commit b7e8d90
src/report.py
```

- A **block start** is a line whose text after trimming leading and trailing whitespace is
  either exactly `commit`, or starts with `commit ` (one space). Everything after that on
  the line is a hash and commit subject; it is never parsed. A block-start line with no
  hash at all (`commit` on its own) is still a block start.
- The **file list** of a block is every other line up to the next block-start line or EOF.
- Lines before the **first** block-start line are ignored entirely.

The file is messy on purpose: two prose lines before the first commit, a header with a
subject after the hash, a path padded with spaces, a tab-indented path, a block that lists
the same path twice, a block with **no** file lines at all, a header with no hash, a file
that only ever appears in one commit, and trailing blank lines.

## Rules

1. **A commit's file set** is the distinct paths in its block: trim surrounding whitespace
   from each line, drop lines that are empty after trimming, and count a repeated path
   once. Order inside a block never matters.
2. **A file's total** is the number of distinct commits whose file set contains it.
3. **Two files are coupled** when they appear together in **at least 2 distinct commits**.
   Their `shared` count is the number of commits that contain both.
4. **The coupling score** of a pair is `shared / (total_a + total_b - shared)` — the Jaccard
   index: shared commits over the commits that touched *either* file. Rounded to 4 decimal
   places and printed with exactly four (`0.5000`, `0.6667`).
5. A block with no files is not counted as a commit anywhere: not in `commits`, not in a
   file's total.
6. Each pair is written once: `file_a` is the **smaller** of the two paths in byte order,
   `file_b` the larger.

## Output

Write exactly these files to `$OUT`:

1. **`out/pairs.csv`** — header `file_a,file_b,shared,score`. One row per coupled pair
   (`shared >= 2`), sorted by `shared` **descending**, then `score` **descending**, then
   `file_a` ascending, then `file_b` ascending. A pair with `shared` below 2 is not in the
   file at all.
2. **`out/summary.json`** — an object with exactly these keys:
   - `commits` — blocks that had at least one file (int)
   - `files` — distinct paths across those blocks (int)
   - `coupled_pairs` — rows in `pairs.csv` (int)
   - `most_coupled` — the `file_a` of the **first** row of `pairs.csv`; the empty string when
     there are no coupled pairs

## Messes to expect

- the two prose lines before the first `commit` line never become paths
- `  src/export.py  ` and `\tsrc/report.py` are `src/export.py` and `src/report.py`
- one block lists `src/export.py` twice: that commit touches it once, so it does not inflate
  the pair counts
- the block whose header is bare `commit` still has files, and they count
- the block with no file lines at all is not a commit: `commits` is smaller than the number
  of `commit` lines
- `src/export.py` and `src/report.py` share 4 commits but are **not** the strongest pair:
  `src/users.py` has fewer commits of its own, so its Jaccard score with `src/export.py` is
  higher even though `shared` ties
- `notes/README.md` appears in exactly one commit, so it is in `files` but in no pair

## Timebox

Five minutes. One pass to build the commit sets, one to count pairs, one sort. If you are
past that, the approach is wrong.
