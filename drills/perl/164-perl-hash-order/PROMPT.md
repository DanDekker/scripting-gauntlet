# 164-perl-hash-order

> "Same input, two different reports, two different orders. The dashboard diffs them and
> pages me. Make the order reproducible."

## Input

`in/events.log` — one event per line: a **user**, whitespace, then an **action**.

```
alice login
bob login
```

## Rules

1. Skip a blank line and a line whose first non-whitespace character is `#`.
2. A line with fewer than two whitespace-separated fields is **invalid**: count it and
   skip it.
3. Count events per user. The user is the first field; case matters.
4. Sort by **count descending**, then by **user ascending in byte order**. The order must
   be identical on every run: nothing may be left to hash order.
5. `top` is the user in the first row, or the empty string when there are no rows.

## Output

Write exactly these files to `$OUT`:

1. **`out/counts.csv`** — header `user,events`, one row per user, sorted as in rule 4.
2. **`out/summary.json`** — an object with exactly these keys:
   - `users` — distinct users (int)
   - `events` — accepted events (int)
   - `invalid` — rejected lines (int)
   - `top` — the user in the first row (string, empty when none)

   Print it as one compact JSON object: `{"users":5,"events":9,"invalid":0,"top":"alice"}`.

## Messes to expect

- `alice` and `bob` both have three events, so the tie-break decides the top row
- users `10` and `9` both have one event, and `10` sorts **before** `9` as text
- hash iteration order changes between runs, so an unsorted solution is not reproducible
- a line with only a bare word is invalid

## Timebox

Three minutes. The comparator needs both keys: count descending **or** name ascending.
