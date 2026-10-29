# 043-sort-unique-count

> "What are we actually logging? Give me the levels with counts, worst first."

## Task

`in/app.log` is one line per event: an ISO timestamp, a level, then a message.

## Rules

1. The level is the **second whitespace-separated field** of the line. Fields are separated
   by runs of spaces or tabs; leading whitespace on a line is irrelevant.
2. **Uppercase** the level before grouping: `error`, `Error` and `ERROR` are the same level.
3. Skip blank lines. Every non-blank line is expected to have a level.
4. Sort by `count` **descending**, then by `level` **ascending** (byte order).

## Output

**`out/levels.csv`** — header exactly `level,count`, one row per distinct level, sorted as in
rule 4. No total row.

**`out/summary.json`** — exactly three keys: `lines` (non-blank lines read),
`levels` (distinct levels), `top` (the level in the first row of the CSV).

## Messes to expect

- the same level in three casings (`ERROR`, `error`, `Error`)
- a level with extra spaces around it
- blank lines
- several low-count levels that all tie at 1

## Timebox

60 seconds. The canonical four-stage pipe: `awk`, `sort`, `uniq -c`, `sort -k1,1nr`.
