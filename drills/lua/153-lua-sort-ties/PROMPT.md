# 153-lua-sort-ties

> "Rank the teams by score. Three of them tied last quarter and the leaderboard kept
> reshuffling between runs, so I need the order pinned down."

## Input

`in/scores.txt` — one record per line:

```
alpha 30
beta 30
```

The file has comment lines, blank lines, and at least one line that is not a record.

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#`.
2. Every other line is a record: a **name**, whitespace, then a **score**. The name is a
   single token with no whitespace. The score is a non-negative integer written in
   decimal. A line that does not match that shape is **invalid**: count it and skip it.
3. Give every accepted record its **index**: its 1-based position among the accepted
   records, counting from 1.
4. Sort the accepted records by **score descending**, numerically. Records with the same
   score keep their **input order**: the one that appeared earlier in the file comes
   first. This must hold every time the script runs.
5. `tied` is the number of accepted records whose score is shared with **another**
   accepted record. Three records that all scored 30 make `tied` 3, not 1.

## Output

Write exactly these files to `$OUT`:

1. **`out/sorted.csv`** — header `name,score,index`, then one row per accepted record in
   the sorted order of rule 4. The `score` column is the plain integer.
2. **`out/summary.json`** — an object with exactly these keys:
   - `records` — how many records were accepted (int)
   - `invalid` — how many lines were invalid (int)
   - `tied` — how many accepted records share their score with another (int)

   Print it as one compact JSON object: `{"records":6,"invalid":1,"tied":5}`.

## Messes to expect

- three records share the score `30` and one pair shares `10`
- `gamma 9` and `delta 10` must not be ordered by their text: `10` outranks `9`
- `zeta abc` is invalid: it is counted and it contributes no score and no tie

## Timebox

Four minutes. The unstable-sort trap is the whole drill: carry the input position
through the sort instead of trusting the order to survive.
