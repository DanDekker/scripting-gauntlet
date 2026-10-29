# 098-todo-harvest

> "I am picking up a repo nobody has touched in months. Give me every TODO in the tree with
> its owner and its line, so I can work out who to ask and what is actually still open."

## Input

`in/tree/` — a directory tree of source and prose files. Every regular file under it is
scanned, whatever its extension, including files that contain no markers at all.

The tree is messy in realistic ways: a `TODO` inside a string literal in the middle of a
line, a lowercase `todo`, a `TODO` in the middle of a prose sentence, a `#TODO` with no space
after the hash, a `- TODO:` markdown bullet, a `TODO_LIST` identifier, a file with no TODOs,
and a line that carries a second marker after the first one.

## Rules

1. **What counts as a marker.** `TODO` is case-sensitive. A marker is the token `TODO` at a
   position where it is not glued to a word on either side (a *word* character is a letter,
   a digit, or `_`), and where one of these holds:
   - it is the first non-blank character of the line, or
   - everything between the line start and the marker ends with a comment marker — `#`, `//`,
     `/*`, `*`, or `--` — followed by one or more spaces or tabs.

   So `    # TODO(pp): x` and `/* TODO: y` and ` * TODO: z` and `-- TODO: w` are markers, and
   `print("TODO: not a marker")`, `#TODO: no space`, `- TODO: bullet`, `TODO_LIST`, and
   `Remember: TODO lists are useful` are not.
2. **One row per line.** A line with two markers is still one TODO; report the **first**
   marker on the line, and the rest of the line stays in `text`.
3. **Owner.** If the marker is immediately followed by `(`, the owner is the text up to the
   next `)`, trimmed. No parentheses means no owner (empty string). An owner of `-` also
   means no owner: report the empty string.
4. **Text.** Everything after the marker, after dropping the owner parenthetical if there was
   one, trimmed. If that starts with `:`, drop the single colon and trim again.
5. **Marker keyword.** Reported upper case: `TODO`.

## Output

Write exactly these files to `$OUT`:

1. **`out/todos.csv`** — header `file,line,marker,owner,text`. One row per TODO. `file` is the
   path relative to `in/tree/` using `/` separators (e.g. `lib/workers/queue.py`). `line` is
   1-based. Sorted by `file` ascending (byte order, so `lib/vendor/...` comes before
   `lib/workers/...`, and `README.txt` before `queue.py`) and then by `line` ascending
   (numeric). `owner` is the empty string when nobody owns the TODO.
2. **`out/summary.json`** — an object with exactly these keys:
   - `files_scanned` — every regular file under `in/tree/`, all extensions (int)
   - `todos` — rows in `todos.csv` (int)
   - `owners` — distinct non-empty owners (int)
   - `orphans` — TODOs with an empty owner (int)
   - `by_marker` — object mapping marker keyword to its count, e.g. `{"TODO": 9}`

## Messes to expect

- `print("TODO: this string is not a marker")` sits mid-line: not a marker, so it is not a row
- `#TODO:` has no space between the hash and the marker: not a marker
- `- TODO: ship it` is a markdown bullet, not a comment: `-` alone is not in the marker list
  (`--` is, so `-- TODO: ...` *is* a marker)
- `TODO_LIST: keep this sorted` stops being a marker at the underscore
- line 5 of `lib/workers/queue.py` has no colon after the owner: `text` simply starts after
  the owner
- `docs/release-notes.md` line 3 has two markers; it is one row, owned by `pp`, and its `text`
  still contains the second `TODO`

## Timebox

Four minutes. If you are past that, the approach is wrong.
