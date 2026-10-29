# 188-perl-context-dispatch

> "A shared query helper needs to return full matching record IDs when called in list context,
> but the match count when called in scalar context. The caller using `my ($first) = query()`
> got the count instead of the first record because the parser assumed one variable meant scalar context."

## Input

`in/records.txt` — whitespace-delimited rows of `<id> <score> <label>`:

```
1 85 alpha
2 40 beta
3 95 gamma
4 60 delta
5 90 epsilon
```

Blank lines and `#` comments are skipped.

## Rules

Implement a subroutine `filter_scores($threshold, @records)` that inspects `wantarray`:
1. In **scalar context** (`!wantarray && defined wantarray`): returns the integer count of records with `score >= threshold`.
2. In **list context** (`wantarray`): returns the list of matching record `id`s (preserving input order).
3. In **void context** (`!defined wantarray`): does nothing and returns empty.

Execute four benchmark queries:
- Query 1: `scalar` context, threshold `70`. Assign to scalar (`my $q1 = filter_scores(...)`).
- Query 2: `list` context, threshold `70`. Assign to array (`my @q2 = filter_scores(...)`).
- Query 3: `list_first` context, threshold `70`. Assign to parenthesized scalar (`my ($q3) = filter_scores(...)`).
- Query 4: `scalar` context, threshold `90`. Assign to scalar (`my $q4 = filter_scores(...)`).

## Output

Write exactly these files to `$OUT`:

1. **`out/dispatches.csv`** — header `caller,context,result`. For array results, join IDs with `;`.
2. **`out/summary.json`** — keys `queries`, `list_queries`, `scalar_queries`. One compact JSON object:
   `{"queries":4,"list_queries":2,"scalar_queries":2}`.

## Messes to expect

- `my ($first) = filter_scores(...)` is **list context** despite the single LHS variable; it receives the first element of the returned list.
- In scalar context, returning `@list` returns the array length, but returning a conditional expression requires explicit `scalar` handling or ternary.

## Timebox

Five minutes. Check `wantarray ? @matches : scalar @matches`.
