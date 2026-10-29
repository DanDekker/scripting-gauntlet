# 157-lua-needle-haystack

> "Somewhere in this log dump is one config line that leaks a value. Find every line that
> carries it, and tell me how many files you could not read as text."

## Input

`in/corpus/` — a directory tree of log files, some in subdirectories. A few of them are
**binary** (they contain a NUL byte) and must not be read as text.

The needle is the exact 10-character string:

```
token=100%
```

## Rules

1. Walk `in/corpus` recursively. Only **regular files** are considered; paths are reported
   relative to `in/corpus` with `/` separators.
2. A file that contains a **NUL byte** (`0x00`) anywhere is **binary**: it is skipped, and
   counted as binary. It is never scanned for the needle and contributes no hits.
3. In a text file, split on `\n`. A trailing `\r` is **kept** as part of the line; it does
   not affect a match that ends before it.
4. Report a hit for a line that contains the needle as a **plain substring**, compared
   case-sensitively. The needle is data, not a pattern: every character in it is literal,
   including `%`, `-` and `.`.
5. One row per matching **line**, not per occurrence: if a line holds the needle twice it
   is still one row, and `column` is the position of the **first** occurrence.
6. `column` is the 1-based **byte** position of the needle's first byte within the line.
7. `line` is the 1-based line number within its file.

## Output

Write exactly these files to `$OUT`:

1. **`out/hits.csv`** — header `path,line,column`, one row per matching line, sorted by
   `path` ascending in **byte order**, then by `line` ascending. No field contains a comma
   or a quote, so plain comma separation is correct.
2. **`out/summary.json`** — an object with exactly these keys:
   - `files` — how many text files were scanned (int)
   - `binary` — how many files were skipped as binary (int)
   - `hits` — how many rows are in `hits.csv` (int)

   Print it as one compact JSON object: `{"files":5,"binary":1,"hits":4}`.

## Messes to expect

- the needle **ends with `%`**, so `string.find(line, needle)` without `plain` raises
  `malformed pattern (ends with '%')` — the whole script dies on the first line it scans
- one file has a NUL byte and contains the needle after it: it is binary, and its match
  must not appear in the output
- one file uses CRLF line endings
- one line contains the needle twice; it produces one row, at the first column
- a file in a subdirectory matches

## Timebox

Four minutes. `string.find(s, needle, 1, true)` is the plain-text form; the fourth
argument is the whole lesson.
