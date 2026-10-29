# 082-atomic-config

> "I am about to rewrite a config a daemon is reading. If I write in place it can read a
> half file. Do it atomically, and refuse the bad update without touching the live one."

## Task

`out/live/app.conf` is the live config (mode `0640`). `in/update.valid` and
`in/update.invalid` are candidate replacements, in that order.

## Rules

1. A candidate is valid when every non-blank, non-`#` line matches
   `^[a-z_][a-z0-9_]*=` (the key is lowercase, with underscores and digits only).
2. Apply the valid candidate **atomically**: create the new content in a temp file in the
   same directory as the target, give it the target's permission bits, then rename it over
   the target. Never open the live file for writing.
3. If a candidate is invalid, do not touch the target. Append one line
   `rejected <file>:<line>` to `out/reject.log`, naming the first offending line.
4. When both candidates are processed, `out/live/` must contain exactly one file,
   `app.conf` - no temp files, no backups.
5. Process the valid candidate first, then the invalid one.

## Output

- `out/live/app.conf` - the applied content, same mode as before.
- `out/reject.log` - one line per rejected candidate.
- `out/summary.json` - exactly three keys: `applied` and `rejected` (booleans), and
  `mode` (the resulting permission bits as an octal string, e.g. `"640"`).

## Messes to expect

- an invalid candidate with an uppercase key and a dash
- a valid update that adds a key
- a leftover temp file in the same directory, which must not survive

## Timebox

4 minutes. `mktemp` in the target directory, `chmod` the old mode, `mv` into place.
