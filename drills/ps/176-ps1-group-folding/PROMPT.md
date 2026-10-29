# 176-ps1-group-folding

> "Two groups differ only by case, and one row has no amount. The rollup merged the groups
> and lost the blank."

## Input

`in/items.csv` — header `id,group,amount`, one row per item. `amount` may be empty.

```
id,group,amount
1,web,10
3,Web,5
```

## Rules

1. Group by `group` **case-sensitively**: `Web` and `web` are different groups.
2. `amount` is a whole number of cents. An empty amount counts as `missing` for that group
   and contributes 0 to its total. A non-numeric amount is a hard error: say which row and
   exit non-zero.
3. `count` is the number of rows in the group, including rows with an empty amount.
4. Sort groups by `group` **ordinal** (byte) order — uppercase letters sort before
   lowercase.

## Output

Write exactly these files to `$OUT`:

1. **`out/groups.csv`** — header `group,count,total,missing`, one row per group.
2. **`out/summary.json`** — an object with exactly these keys: `groups`, `items`,
   `missing`. One compact JSON object: `{"groups":4,"items":6,"missing":2}`.

## Messes to expect

- `web` and `Web` are separate groups with totals 10 and 5
- `cache` has one row and an empty amount: count 1, total 0, missing 1
- `Group-Object` without `-CaseSensitive` merges the two web groups — the bug this drills
- ordinal order puts `Web` first, while culture order would put `cache` first
- a pipeline that filters on the amount drops the empty row and undercounts

## Timebox

Five minutes. `-CaseSensitive` on the grouping, and count the rows you saw, not the ones
that survived a filter.
