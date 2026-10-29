# 039-count-lines

> "How many lines are in each of the app logs? Quick, before standup."

## Task

`in/` holds a handful of `*.log` files. Count the lines in each one.

## Rules

1. Consider only files matching `in/*.log`. Ignore everything else in `in/` (there is a
   `notes.md` in there that is not a log).
2. A **line** is a newline-terminated record, **plus** a final record that has no trailing
   newline. A file that does not end with `\n` still has its last line counted — this is
   exactly where `wc -l` undercounts. An empty file has 0 lines.
3. Blank lines count as lines.
4. Windows line endings (`\r\n`) do not change the count.
5. Report each file by its **base name**, no directory prefix.

## Output

**`out/linecounts.csv`** — header exactly `file,lines`, then one row per log file sorted by
`file` **ascending** (byte order), `lines` a plain integer.

**`out/total.json`** — exactly two keys: `files` (how many log files) and `lines` (sum of
all the counts). Both integers.

## Messes to expect

- one file with no trailing newline (the whole point of the drill)
- one empty file
- a blank line in the middle of a file
- CRLF line endings in one file
- a `notes.md` that must not appear in the output

## Timebox

90 seconds. `awk 'END{print NR}'` per file beats `wc -l` here, and that is the lesson.
