# 060-nul-manifest

> "I need a trustworthy inventory of this exported folder. Some filenames came from
> users, so please don't assume they behave nicely in a line-oriented loop."

## Task

Walk `in/tree/` recursively and report each regular file's relative path, byte count,
and SHA-256 content hash. Do not follow links or include directories.

## Output

**`out/manifest.json`** — a JSON array sorted by `path` ascending. Each object has
exactly `path` (tree-relative path with `/` separators), `bytes` (integer), and
`sha256` (lowercase 64-character hex digest). An empty file has the SHA-256 digest of
empty content. Preserve every character in each path, including tabs and newlines.

**`out/summary.json`** — exactly three integer keys: `files`, `bytes` (sum of file
sizes), and `empty` (zero-byte files).

If a file cannot be read or hashed, name it on stderr and exit non-zero.

## Messes to expect

- a leading-dash filename, a hidden filename, and a name with spaces and parentheses
- one filename containing a tab and another containing a newline
- a nested directory and an empty file

## Timebox

4 minutes. `find -print0` into a Bash `read -d ''` loop; `jq` handles JSON escaping.
