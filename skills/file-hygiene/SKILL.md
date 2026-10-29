---
name: file-hygiene
description: Triage, dedupe, rename, and resort messy directories — downloads folders, photo dumps, exports, and years of final_FINAL names. Use when asked to clean up a directory, find duplicate files, sort files by type or date, normalize filenames, or find junk files. Always inventory and dry-run before moving anything. Not for filesystem-level recovery or permission repair.
license: MIT
metadata:
  family: file-hygiene
  drill: 005-dir-hygiene
---

# File hygiene

`mv` and `rm` are not reversible. Everything here is ordered so that the destructive step
is last and auditable.

## 1. Inventory before you touch anything

```bash
find . -type f -printf '%s\t%p\n' | sort -rn | head -20      # GNU
find . -type f -exec stat -f '%z%t%N' {} + | sort -rn | head  # BSD/macOS
```

Know the count, the total size, and the outliers before you know the plan.

## 2. Print the plan, then execute it

Generate `original → destination` lines, review them, *then* move. The same script gains a
`--apply` flag or a `while read` loop over the reviewed plan.

```bash
while IFS=$'\t' read -r src dst; do
  printf 'mv %q %q\n' "$src" "$dst"          # dry run
  # mkdir -p "$(dirname "$dst")"; mv "$src" "$dst"
done < plan.tsv
```

## 3. Dedupe by content, not name

Two files with the same bytes and different names are one file; two files with the same
name and different bytes are two files. Hash, group, keep one — and state the rule you
used to pick the keeper (shortest path? newest? highest resolution?).

```bash
find . -type f -exec shasum -a 256 {} + | sort | awk '{ h=$1; if (!(h in k)) { k[h]=$2; print $2 } }'
```

`sha256sum` on Linux, `shasum -a 256` on macOS — detect, don't assume.

## 4. Normalize with a rule you can state

Lowercase; whitespace runs → single `-`; drop characters outside `[a-z0-9._-]`; collapse
repeated `-`. Ambiguity here is how you overwrite two files with one name.

**Always detect collisions after normalizing** and disambiguate (`-2`, or keep the hash
prefix). Flattening a tree is the usual source of them.

## 5. Junk that is always junk

| pattern | what it is |
| --- | --- |
| `.DS_Store` | macOS Finder metadata |
| `Thumbs.db`, `desktop.ini` | Windows Explorer metadata |
| `~$*` | Office lock files (the real doc has no `~$`) |
| `*.crdownload`, `*.part` | interrupted downloads |
| zero-byte files | usually truncated copies — count them before deleting |

## 6. Write a manifest

`original,clean,sha256,bytes`, sorted. It turns "I moved your files" into an auditable
statement, and it is the only thing that lets someone undo your work.

## Traps

- **Copy, don't move,** when the user says "don't delete anything I can't get back".
- **Case-insensitive filesystems.** `Report.pdf` and `report.pdf` collide on macOS/Windows
  and not on Linux. Test on the target.
- **Symlinks** — `find -type f` skips them; `-L` follows (and can loop).
- **Newlines and tabs in filenames.** `find -print0` + `read -d ''`, never `for f in $(ls)`.
- **Preserving metadata** — `cp -p` or `rsync -a` if timestamps matter to the user.
- **GNU vs BSD flags.** `stat -c` vs `stat -f`, `sed -i` vs `sed -i ''`. See
  [references/gnu-vs-bsd.md](references/gnu-vs-bsd.md).

Prove it against `drills/005-dir-hygiene`.
