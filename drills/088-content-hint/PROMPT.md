# 088-content-hint

> "I remember a line from a note: 'the quarterly review is scheduled'. I don't remember
> which file, or the exact capitalisation. Find it."

## Task

`in/query.txt` holds the remembered line. `in/notes/` holds the notes.

## Rules

1. Scan `.md`, `.txt` and `.log` files recursively; skip dot-directories.
2. Skip files larger than 1 MB and count them in `skipped_large`.
3. Matching is case- and whitespace-insensitive: lowercase the line, collapse every run
   of spaces/tabs to one space, trim; do the same to the query. A line matches when the
   normalised query appears anywhere in it.
4. Report the **original** line, trimmed of surrounding whitespace.
5. Order by path ascending, then line number ascending.

## Output

- `out/matches.csv` - header `path,line,text`, one row per matching line, path relative to
  `in/notes/`.
- `out/match.json` - exactly three keys: `path`, `line`, `text` for the first match.
- `out/summary.json` - exactly four integers: `files_scanned`, `matching_files`,
  `matching_lines`, `skipped_large`.

## Messes to expect

- the same words in a different order
- `was scheduled` instead of `is scheduled`
- double spaces inside the line you want
- a 2 MB log that must be skipped, not searched

## Timebox

3 minutes. Normalise both sides, then substring-test.
