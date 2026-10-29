# 029-set-ops

> "Two exports of user ids. I need everyone, the overlap, and what's only on each side."

## Task

`in/a.txt` and `in/b.txt` are one id per line, with duplicates, blanks and case noise.

## Rules

1. Normalize every id: **trim**, **lowercase**, and drop the line if it is empty after
   trimming.
2. Each file is a **set** — duplicates collapse.
3. `both` is the intersection, `only_a` is A minus B, `only_b` is B minus A, `union` is
   everything.
4. Every output list is sorted **ascending** with no header line and no blank lines.

## Output

- **`out/union.txt`**
- **`out/both.txt`**
- **`out/only_a.txt`**
- **`out/only_b.txt`**
- **`out/summary.json`** — exactly six keys: `a`, `b`, `union`, `both`, `only_a`, `only_b`
  (all counts of distinct ids).

## Messes to expect

- an id repeated inside one file
- an id padded with trailing spaces
- a blank line
- the same id in different case in the two files

## Timebox

3 minutes. Normalize to a sorted unique list per side, then `comm -12/-13/-23`.
