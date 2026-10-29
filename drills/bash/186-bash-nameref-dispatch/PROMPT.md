# 186-bash-nameref-dispatch

> "Incoming operational metrics arrive categorized under different namespaces. We need to
> dynamically route each record into its category bucket and update tallies in-place."

## Input

`in/actions.txt` — whitespace-delimited rows of `<category> <metric> <amount>`:

```
alpha cpu 10
beta mem 20
alpha cpu 5
gamma disk 100
beta io 3
alpha mem 4
gamma disk 50
```

Blank lines and `#` comments are skipped.

## Rules

1. Parse each valid line into category, metric name, and integer amount.
2. Route the update to an associative bucket named after the category (e.g. `bucket_<category>`).
3. Updates must be executed via a reusable function taking the bucket variable name as a nameref
   (`local -n ref=$1`) and modifying the caller's bucket in-place.
4. Export rows sorted by `category` ascending, then `metric` ascending.

## Output

Write exactly these files to `$OUT`:

1. **`out/tallies.csv`** — header `category,metric,total`.
2. **`out/summary.json`** — keys `categories`, `entries`, `total`. One compact JSON object:
   `{"categories":3,"entries":5,"total":192}`.

## Messes to expect

- Multiple entries for the same metric in a category must accumulate (`alpha cpu` is 10 + 5 = 15).
- Categories must be dynamically dispatched without giant hardcoded copy-paste blocks.
- Using `${!var}` (indirect expansion) fails on array subscript assignments; bash namerefs (`local -n`)
  are required for direct array reference.
- Parameter names in the helper must not collide with caller variable names (e.g. using `local -n target=$1`
  when `$1` is `target` causes circular nameref errors).

## Timebox

Five minutes. Declare associative arrays per category and pass their variable names to a nameref helper.
