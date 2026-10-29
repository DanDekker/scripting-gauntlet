# 081-manifest-drift

> "Two release manifests, one deploy apart. What appeared, what vanished, what changed
> under the same name, and what can I ignore?"

## Task

`in/old.json` and `in/new.json` are manifests: a JSON array of objects with `path`,
`bytes` and `sha256`, already sorted by path. Compare them.

## Rules

1. A path only in `new.json` is `added`; only in `old.json` is `removed`.
2. A path in both is `changed` when the `sha256` differs, otherwise `unchanged`.
   Size alone never decides: a same-size edit is still changed.
3. `from_bytes` is the old size (empty for `added`), `to_bytes` is the new size (empty
   for `removed`).
4. Report every path that is not `unchanged`, sorted ascending in byte order.
5. A manifest that is not a JSON array of objects with those three keys is an error:
   name the file on stderr and exit non-zero.

## Output

- `out/drift.csv` - header `path,change,from_bytes,to_bytes`.
- `out/summary.json` - exactly four integers: `added`, `removed`, `changed`, `unchanged`.

## Messes to expect

- a file edited in place with the same byte count (must be `changed`)
- a path with spaces
- a brand-new file and a deleted file
- many untouched files that must not leak into the report

## Timebox

3 minutes. Load the old side into a map, walk the new side, then flush the leftovers.
