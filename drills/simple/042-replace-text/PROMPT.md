# 042-replace-text

> "We moved the API. Every mention of the old host in the configs and docs has to say
> `api.internal` now. Please don't touch anything else."

## Task

Every file under `in/` mentions the old API host, `api.example.com`, somewhere. Rewrite
the tree with the new host.

## Rules

1. Replace the **literal** string `api.example.com` with `api.internal`. It is a literal,
   not a pattern: `apiXexample.com` must survive untouched, and so must anything else that
   merely *looks* like a match to a regex.
2. Replace **every** occurrence on a line, not just the first.
3. Only that string changes. Every other byte of every file is preserved.
4. Copy **every** file under `in/`, whether it changed or not, into `out/tree/` at the same
   relative path. Directories are recreated as needed.
5. Do not edit `in/`.

## Output

- **`out/tree/<same relative path>`** — the rewritten copy of each input file.
- **`out/changed.txt`** — relative paths (same form as under `out/tree/`) of the files that
  actually changed, one per line, sorted **ascending** byte order. Unchanged files are not
  listed.
- **`out/summary.json`** — exactly three keys: `files_scanned` (every file under `in/`),
  `files_changed`, and `replacements` (total occurrences replaced across the whole tree).

## Messes to expect

- a line with two occurrences of the old host
- `apiXexample.com` — a decoy that an unescaped `sed 's/api.example.com/.../'` rewrites
- a file with no match at all (it still gets copied, and must not be listed as changed)
- files in nested directories

## Timebox

90 seconds. `find` plus one `sed 's/api\.example\.com/api.internal/g'`.
