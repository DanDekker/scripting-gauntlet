# 005-dir-hygiene

> "This folder is years of 'final_FINAL'. Don't delete anything I can't get back —
> just sort out the duplicates and the junk, and give me a list of what moved where."

## Task

`in/messy/` is a directory tree. Produce a tidied copy at `out/clean/` and a manifest
that accounts for every file you kept.

**Never modify `in/`.** Work from it, write to `out/`.

## Rules

1. **Drop junk.** These never survive, wherever they are:
   - `.DS_Store`, `Thumbs.db`
   - files whose name starts with `~$` (Office lock files)
   - zero-byte files
2. **Dedupe by content**, not by name. Two files with identical bytes are one file.
   Keep the one with the **shortest original path** (relative to `in/messy/`); break ties
   with the lexicographically smallest path. The rest are dropped.
3. **Normalize the name:** lowercase it; replace each run of whitespace with a single
   `-`; drop any character that is not `a-z`, `0-9`, `.`, `_`, or `-`; collapse repeated
   `-`. The extension stays.
4. **Resort by extension** into a lowercase subdirectory: `txt/`, `md/`, `jpg/`, `pdf/`,
   `csv/`. The extension is the part after the final dot, lowercased, without the dot.
   Files with no extension go in `noext/`.
5. Flatten: everything lands one level deep in `out/clean/<ext>/<name>`. Subdirectory
   structure is not preserved.

## Output

**`out/clean/<ext>/<name>`** — the surviving files, copied (not moved).

**`out/manifest.csv`** — header plus one row per surviving file, sorted by `original`
ascending (byte order):

```
original,clean,sha256,bytes
```

- `original` — path relative to `in/messy/`, e.g. `deep/nested/data.csv`
- `clean` — path relative to `out/clean/`, e.g. `csv/data.csv`
- `sha256` — lowercase hex of the file content
- `bytes` — size of the file

## Messes to expect

- the same bytes under two different names, and under two different extensions
- a nested directory you must flatten
- zero-byte debris
- a name with spaces and capitals
- macOS and Windows junk files

## Timebox

5 minutes. `find` + `shasum` + a sort, or `os.walk` + `hashlib`. Print the plan first if
you are moving rather than copying — `mv` is not reversible.
