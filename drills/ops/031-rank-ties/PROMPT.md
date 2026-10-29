# 031-rank-ties

> "Rank the scores. Ties share a place, and I want to know if the next rank skips a number."

## Task

`in/scores.csv` has `name,score` rows, with ties.

## Rules

1. `name` and `score` are trimmed. `score` is an integer.
2. Sort by `score` **descending**, ties by `name` **ascending**.
3. **`rank`** is competition rank: the position of the first row of that score. Ties share it,
   and the rank after a tie skips the numbers the ties used (`1, 1, 3`).
4. **`dense_rank`** counts distinct scores seen so far, starting at 1 (`1, 1, 2`).

## Output

**`out/ranked.csv`** — header exactly `name,score,rank,dense_rank`, one row per player, in the
sort order from rule 2.

**`out/summary.json`** — exactly three keys: `players`, `top_score`, `distinct_scores`.

## Messes to expect

- three players on the same score
- a padded score (` 88`)
- a blank line inside the file
- one player alone on a score, so the competition rank skips

## Timebox

3 minutes. Sort once; while streaming keep `previous score` and a position counter.
