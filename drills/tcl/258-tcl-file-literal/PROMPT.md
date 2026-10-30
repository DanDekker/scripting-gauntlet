# 258-tcl-file-literal

> "Read the exact files named in this manifest. Brackets and a star are part of the
> names, not glob syntax."

## Input

in/manifest.txt lists:

~~~text
*.cfg
[draft].txt
nested/notes file.txt
~~~

The files live under in/tree. Their contents are cfg, draft, and note, each with a
final newline.

## Rules

1. Resolve each path with file join relative to in/tree.
2. Open the exact path and record its byte size and trimmed first line.
3. Preserve manifest order. Do not glob or discover files.

## Output

Write out/files.csv with header path,bytes,first_line and three rows.
Write out/summary.json with exactly {"files":3,"bytes":15}.

## Messes to expect

- glob treats *.cfg and [draft].txt as patterns
- file join and open take the manifest value literally
- a nested filename contains a space
- the final newline counts in the byte size but not in first_line

## Timebox

Four minutes. Use file join, file size, and open; glob is the wrong primitive.
