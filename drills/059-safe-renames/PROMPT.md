# 059-safe-renames

> "These filenames need tidying, but two of them swap names. Please apply the whole
> list without losing either file."

## Task

`in/tree/` is a flat directory. `in/renames.tsv` has `from<TAB>to` rows, with no
header. Apply the rename plan to a **copy** of the tree in `out/tree/`.

## Rules

1. Skip empty lines and lines beginning with `#` in the plan.
2. Every source must be a regular file in the input tree. Source and destination
   names are flat filenames: no `/`, tab, comma, or newline.
3. A destination may already exist **only if it is also a source** in the plan. This
   allows swaps and chains. Reject duplicate sources or destinations.
4. Check the entire plan before moving anything. On a bad row, print the offending
   name or row and exit non-zero.
5. Stage all sources under `$WORK` first, then install their destinations. Files not
   mentioned as sources stay untouched. Preserve file contents.

## Output

- `out/tree/`: the renamed flat tree, with no temporary files.
- `out/moves.csv`: header `from,to`, one row per applied rename, sorted by `from`
  ascending in byte order (`LC_ALL=C`).
- `out/summary.json`: exactly `moved` (rename rows) and `untouched` (input files not
  named as sources), both integers.

## Messes to expect

- blank and comment lines in the plan
- two filenames that swap places, so a direct sequence of `mv` commands loses data
- a filename with spaces and parentheses, and one beginning with `-`
- one file that must remain untouched

## Timebox

5 minutes. Two `mv` loops are simpler than trying to find a safe rename order.
