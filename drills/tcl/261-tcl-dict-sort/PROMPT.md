# 261-tcl-dict-sort

> "Roll up these repeated counters and give me a reproducible ranking. Higher totals
> come first; ties use the key's ordinary string order."

## Input

in/counts.tsv has key and integer count rows:

~~~text
key	count
api	3
web	2
api	1
cache	2
~~~

## Rules

1. Aggregate duplicate keys with dict.
2. Sort totals descending.
3. Break equal totals with string compare ascending.
4. Do not rely on dict iteration order.

## Output

Write out/counts.csv with header key,count and rows:

~~~csv
api,4
cache,2
web,2
~~~

Write out/summary.json with exactly {"keys":3,"total":8}.

## Messes to expect

- api appears twice and must be accumulated
- cache and web tie
- dict iteration order is not the report's ranking
- a total ordering makes repeated runs and diffs reproducible

## Timebox

Five minutes. Turn dict entries into a list and use lsort with an explicit comparator.
