# 169-ruby-sort-mixed

> "Half the scores are numbers, half are quoted numbers from the CSV, and three are blank.
> `sort` blew up on the blank ones and the tie order changes between runs."

## Input

`in/records.jsonl` — one JSON object per line: a `name`, and a `score` that may be a
number, a numeric **string**, `null`, or absent.

```
{"name": "a", "score": 10}
{"name": "b", "score": "9"}
{"name": "c", "score": null}
```

## Rules

1. Skip a blank line.
2. A `null` or absent `score` is **missing**: it is still ranked, at the bottom.
3. A string score must be pure decimal text (`^-?[0-9]+(\.[0-9]+)?$`) to count. Anything
   else (`"abc"`, `""`) is **invalid**: counted and excluded from the ranking.
4. Rank by score **descending**, numerically — `"10"` beats `"9"` because ten is more
   than nine.
5. Ties are broken by **input order**: the record that appeared first ranks first. Do not
   assume `sort_by` is stable.
6. Ranks are 1-based and consecutive.

## Output

Write exactly these files to `$OUT`:

1. **`out/ranked.csv`** — header `rank,name,score`, one row per ranked record. Write the
   score as a plain number (`10`, `9`, `2.5`); a missing score is an empty field.
2. **`out/summary.json`** — an object with exactly these keys:
   - `lines` — non-blank lines (int)
   - `ranked` — rows in `ranked.csv` (int)
   - `invalid` — records with a non-numeric string score (int)
   - `missing` — ranked records with a null or absent score (int)

   Print it as one compact JSON object: `{"lines":7,"ranked":6,"invalid":1,"missing":2}`.

## Messes to expect

- three records score `10` (one as a number, two as strings) and must keep input order
- `"9"` is text that must lose to `"10"`, not win by byte order
- `"abc"` is invalid: excluded, counted once
- one record has `"score": null` and one has no `score` key: both rank last, both count as
  missing

## Timebox

Three minutes. Sort on a tuple: `[missing_flag, -score, input_index]`.
