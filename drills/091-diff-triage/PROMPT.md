# 091-diff-triage

> "Review this pull request diff before you approve anything. Tell me which files
> changed, how big each change is, and which ones need a human to look twice."

## Input

`in/changes.diff` — a unified diff (git style, `diff --git` headers).

It may contain, in any order:

- normal text hunks (`@@` headers, `+`/`-`/` ` lines)
- `new file mode` entries (the old side is `/dev/null`)
- `deleted file mode` entries (the new side is `/dev/null`)
- `old mode` / `new mode` pairs (permission or type changes)
- `Binary files ... differ` entries (no text hunks at all)

## Rules

For every file that appears in the diff, compute:

- `path` — the path after the `b/` prefix of the `+++` line. For a binary entry there is
  no `+++` line, so take the path from the `diff --git a/<path> b/<path>` header.
- `added` — number of lines starting with `+`, **excluding** the `+++` header. An added
  empty line (a bare `+`) counts as one added line.
- `deleted` — number of lines starting with `-`, **excluding** the `---` header.

Attach every flag that applies (a file can have several):

| flag | when |
| --- | --- |
| `binary` | the entry has a `Binary files ... differ` line |
| `deleted` | the file was removed: a `deleted file mode` line, or the new side is `/dev/null` |
| `large` | `added + deleted` is 100 or more |
| `mode-change` | the entry has `old mode` / `new mode` |
| `new` | the file was added: a `new file mode` line, or the old side is `/dev/null` |
| `secret` | an added line looks like a leaked credential |

A line looks like a leaked credential if the added line (case-insensitively) contains any
of: `api_key`, `api-key`, `password`, `secret`, or `-----begin`.

Flags are emitted in alphabetical order, joined with `;`.

## Output

1. **`out/risk.csv`** — header `path,added,deleted,flags`. One row per file in the diff,
   sorted by `path` ascending. `flags` is the `;`-joined flag list, or empty when the
   file has no flags.
2. **`out/summary.json`** — object with keys:
   - `files`: number of files in the diff
   - `total_added`: sum of `added`
   - `total_deleted`: sum of `deleted`
   - `flagged_files`: number of files with at least one flag
   - `top_risk`: the path carrying the most flags; ties go to the lexicographically
     smallest path (empty string when no file has any flag)

## Messes to expect

- the `+++`/`---` header lines must not be counted as content
- binary entries have no `+++` line at all
- a deleted file has hunks, so it has a nonzero `deleted` count

## Timebox

A few minutes. If you are past that, the approach is wrong.
