# 135-git-conflict-markers

> "A merge went sideways and nobody noticed — the markers are still in the tree. Walk the
> repo, tell me every file that still has a real conflict in it, where each block starts
> and ends, and how much of each side is in there. Do not count the ones in the docs."

## Input

`in/repo/` — a directory tree of source and text files (`.py`, `.ts`, `.js`, `.md`,
`.json`, `.yml`, …). Scan it **recursively**, including dot-directories such as
`.github/`.

## What a conflict block is

A genuine conflict block is the three-part agreement git leaves behind:

```
<<<<<<< HEAD
our changes
=======
their changes
>>>>>>> branch-feat
```

and the `diff3`/`zdiff3` variant, which adds a base section that belongs to neither side:

```
<<<<<<< HEAD
our changes
||||||| base
ancestor
=======
their changes
>>>>>>> branch-feat
```

Rules, exactly:

1. **Column 1 only.** A marker line is one that *starts* with `<<<<<<< `, `||||||| `,
   `>>>>>>> ` (seven characters then a space) or is `=======` optionally followed by
   spaces/tabs. Indented markers — a markdown code block, an indented snippet in a
   document — are **not** markers and never form a block.
2. **Completeness.** A block starts at a `<<<<<<< ` line, must pass through a `=======`
   line (with or without a `||||||| ` base line before it) and must be closed by a
   `>>>>>>> ` line. Anything else is **orphaned** and is not reported: a `<<<<<<< ` with no
   `=======`, or with no closing `>>>>>>>` before the file ends, is not a conflict.
3. **Abandon and restart.** If a new `<<<<<<< ` line appears while a block is still open,
   the open block is orphaned; the new line starts a fresh block.
4. **Counting lines.** `our_lines` counts the lines strictly between `<<<<<<< ` and the
   `=======` line, or between `<<<<<<< ` and the `||||||| ` line when a base section is
   present. `their_lines` counts the lines strictly between `=======` and `>>>>>>> `. The
   `||||||| ` base section is counted by neither side. Marker lines themselves are never
   counted.
5. **Labels.** `our_branch` is everything after `<<<<<<< ` on the start line, with leading
   and trailing whitespace trimmed. `their_branch` is everything after `>>>>>>> ` on the
   end line, trimmed — so `>>>>>>> 1a2b3c4d (feat: retry policy)` yields exactly
   `1a2b3c4d (feat: retry policy)`; the hash is not stripped.
6. **Files.** `files_scanned` counts every regular file under `in/repo/`, conflicted or
   not, dot-files included. A file that is not valid UTF-8 is scanned (it counts) and can
   never contain a conflict.

## Output

1. **`out/conflicts.csv`** — header `file,start_line,end_line,our_branch,their_branch,our_lines,their_lines`.
   One row per complete conflict block. `file` is the path **relative to `in/repo/`**, using
   `/` separators and no leading `./`. `start_line` is the 1-based line number of the
   `<<<<<<< ` line, `end_line` the 1-based line number of the `>>>>>>> ` line.
   Rows are sorted by `file` ascending (byte order), then by `start_line` numeric
   ascending. A file with several blocks gets several rows.
2. **`out/summary.json`** — object with exactly these keys:
   - `files_scanned` (int) — regular files under `in/repo/`
   - `conflicted_files` (int) — distinct files with at least one complete block
   - `total_conflicts` (int) — complete blocks across the tree
   - `clean_files` (int) — `files_scanned - conflicted_files`
   - `max_conflict_lines` (int) — the largest `our_lines + their_lines` of any block, or
     `0` when there are no conflicts

## Messes to expect

- `notes.txt` has a `<<<<<<< HEAD` with no `=======` at all, and `src/truncated.py` has the
  start and the separator but the file ends before any `>>>>>>>`. Both are orphans: zero
  rows, and both files count as clean.
- `docs/merge-notes.md` shows a full three-marker example, but indented four spaces —
  documentation, not a merge.
- `src/app.py` has two separate blocks, one of them `diff3`; the base line belongs to
  neither side.
- `src/legacy.js` carries trailing spaces after `=======` and after a label that ends with
  a commit hash and a parenthesised title.
- `.github/workflows/ci.yml` is a dot-directory file: skipping hidden paths loses a
  conflict and one scanned file.

## Timebox

A few minutes. If you are past that, the approach is wrong.
