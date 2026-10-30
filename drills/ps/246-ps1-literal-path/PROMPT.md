# 246-ps1-literal-path

> "Inventory these four files from a handoff directory. The names are literal, even
> when they look like PowerShell wildcard patterns or begin with a dash."

## Input

in/tree contains:

- -dash.txt
- [plan].txt
- *.log
- nested/notes.txt

in/manifest.csv lists those relative paths in that order. The bracket, star, and dash
characters are part of the filenames.

## Rules

1. Read each manifest path literally, relative to in/tree.
2. Do not recurse or discover extra files; follow manifest order.
3. Record the byte length and the first line with its surrounding whitespace removed.

## Output

Write exactly:

1. out/inventory.csv with header path,bytes,first_line and four rows.
2. out/summary.json with exactly {"files":4,"bytes":49}.

## Messes to expect

- [plan].txt is a wildcard character class to PowerShell unless -LiteralPath is used
- *.log is a wildcard that would match a set of names instead of one file
- a path beginning with - is data here, not a parameter
- the manifest order is the required order

## Timebox

Four minutes. Use -LiteralPath for both Get-Item and Get-Content.
