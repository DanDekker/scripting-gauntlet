# 123-review-checklist

> "Before I read this diff line by line: which lines would I flag in review, and with what?
> Only the added ones — I don't care that the old code was worse."

## Input

`in/changes.diff` — a unified diff, git style: `diff --git a/<path> b/<path>` headers,
`@@` hunk headers, and ` ` / `+` / `-` content lines.

## Rules

A **finding** is one `(file, line, code)` triple. `line` is the **1-based line number in
the diff file**, not a line number inside the source file.

Only **added** lines are inspected: a line starting with `+` that is not the `+++` header.
A `-` line (including the `---` header) is never a finding.

| code | when |
| --- | --- |
| `trailing-whitespace` | the added diff line ends with a space or a tab |
| `long-line` | the added diff line is longer than 100 characters, counting the leading `+` |
| `todo` | the added line contains `TODO` or `FIXME`, uppercase only |
| `debug` | the added line contains `console.log` or `print(` |
| `hardcoded-endpoint` | the added line contains a URL (`http://` or `https://`) or an IPv4 address |

One added line can trip several codes — emit a row for each. An added line that trips
none emits nothing.

An **IPv4 address** is four dot-separated decimal numbers, each in 0–255, that is not
part of a longer run of digits and dots: `10.0.0.12` is one, `999.300.1.1` is not (the
parts are out of range), and `1.2.3` is not (three parts).

**The file of a finding** is the path after `b/` on the `+++` line of that file's entry.
For a deleted file the `+++` line is `/dev/null`, so the path comes from the
`diff --git a/<path> b/<path>` header instead.

## Output

Write exactly these files to `$OUT`:

1. **`out/findings.csv`** — header `file,line,code`. One row per finding, sorted by
   `file` ascending (byte order), then `line` ascending, then `code` ascending.
2. **`out/summary.json`** — an object with exactly these keys:
   - `files` — distinct files in the diff (int)
   - `lines_added` — added lines counted across the whole diff, `+++` headers excluded (int)
   - `findings` — total rows in `findings.csv` (int)
   - `by_code` — object mapping each code that actually occurs to its count; a code with
     zero findings is **absent** from the object
   - `files_flagged` — number of files with at least one finding (int)

## Messes to expect

- a deleted line carrying `console.log`, and a deleted `// FIXME` line: neither is a finding
- a deleted file: its `+++` is `/dev/null`, so the file name must come from the `diff --git`
  header, and it has no added lines at all
- a line indented with a tab that trips nothing, and another line that *ends* with a tab
  and trips `trailing-whitespace`
- a one-line `+` (an added blank line): length 1, no trailing whitespace, no finding
- a comment line (`+// TODO: ...`) — a TODO in a comment is still a finding
- `999.300.1.1` next to a real `10.0.0.12`: only the real one is a hardcoded endpoint
- a 109-character added line, and a file (`docs/notes.md`) with no findings at all

## Timebox

Four minutes. One pass over the diff, a list of `(file, line, code)`, then sort.
