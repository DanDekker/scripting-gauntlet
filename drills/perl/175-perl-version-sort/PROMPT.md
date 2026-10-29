# 175-perl-version-sort

> "The release board is sorted newest first and it keeps putting 1.9.9 above 1.10.2."

## Input

`in/releases.txt` — one release per line: `name version`.

```
alpha 1.10.2
beta 1.9.9
```

Blank lines and lines starting with `#` are skipped.

## Rules

1. A version is valid only when it is dotted decimal text: `^[0-9]+(\.[0-9]+)*$`.
   Anything else (`beta`, `1.x`) is **invalid**: counted and excluded.
2. Compare versions **component by component, numerically**: `1.10.2` is newer than
   `1.9.9`, and `1.2.10` is older than `1.9.9`.
3. Sort by version **descending**, then by name ascending (byte order) when versions tie.
4. Ranks are 1-based and consecutive.

## Output

Write exactly these files to `$OUT`:

1. **`out/ordered.csv`** — header `rank,name,version`, one row per valid release, sorted as
   in rule 3.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — non-blank lines (int)
   - `ordered` — rows in `ordered.csv` (int)
   - `invalid` — releases whose version is not dotted decimal (int)
   - `newest` — the name in the first row, or `""` when there are no rows (string)

   One compact JSON object: `{"lines":7,"ordered":6,"invalid":1,"newest":"gamma"}`.

## Messes to expect

- three releases share `1.10.2` and must come out in name order
- `1.9.9` must sort **above** `1.2.10` even though `"1.9.9" lt "1.2.10"` is false in
  string terms
- `zeta beta` has a non-numeric version: invalid, not last
- `2.0.0` is the newest release

## Timebox

Four minutes. `version->parse($v) <=> version->parse($w)` is the core-module route;
splitting on dots and comparing integers is the other.
