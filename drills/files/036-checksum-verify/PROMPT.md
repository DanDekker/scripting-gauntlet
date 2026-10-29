# 036-checksum-verify

> "I signed a manifest before I handed the box over. Something has drifted since —
> tell me exactly what, then re-sign what is actually there now."

## Task

`in/manifest.sha256` is the manifest of `in/src/` taken **before** the drift.
`in/src/` is what is on disk **now**. Compare them in both directions, then rebuild
the manifest.

## Rules

1. Manifest line format is `<sha256>  <path>`: 64 lowercase hex characters, **two**
   spaces, then the path relative to `in/src/` with forward slashes. Ignore blank lines.
2. Classify **every** path that appears in the manifest or on disk, exactly once:
   - `MISSING` — in the manifest, not on disk
   - `EXTRA` — on disk, not in the manifest
   - `MODIFIED` — in both, hashes differ
   - `MATCH` — in both, hashes equal
3. Hash file **contents** byte for byte. No normalising line endings, no skipping.
4. `expected` is the manifest's hash (empty for `EXTRA`). `actual` is the hash of the
   file on disk (empty for `MISSING`).
5. A path is never reported twice.

## Output

**`out/verify.csv`** — header exactly `path,status,expected,actual`, one row per path,
sorted by `path` ascending (byte order).

**`out/rebuilt.sha256`** — the manifest of what is on disk **now**: one line per file as
`<sha256>  <path>` (same two spaces), sorted by `path` ascending. `path` is relative to
`in/src/`.

**`out/summary.json`** — exactly six keys:

- `manifest` — entries in the signed manifest
- `match`, `missing`, `modified`, `extra` — counts per status
- `ok` — boolean, `true` only when `missing`, `modified` and `extra` are all zero

## Messes to expect

- a file whose content changed by a single line
- a file that was deleted after signing
- a file that appeared after signing
- a path with a space in it
- nested directories
- a manifest that does not mention the new file at all

## Timebox

3 minutes. `find -print0` + one hash call per file, then an awk join on the manifest.
Detect `sha256sum` vs `shasum -a 256` — macOS does not ship the first.
