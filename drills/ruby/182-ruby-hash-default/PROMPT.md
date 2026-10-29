# 182-ruby-hash-default

> "Per-user tags. The first version printed an empty tag column for every user and the
> hash had no keys at all."

## Input

`in/events.txt` — one event per line: a **user**, whitespace, then a **tag**.

```
alice login
bob view
```

Blank lines and `#` comments are skipped.

## Rules

1. Count events per user and collect that user's tags.
2. Report `tags` as the user's tags sorted ascending, joined with `;` (duplicates kept).
3. Sort rows by user ascending.
4. A user's bucket must exist as a real key after the first read.

## Output

Write exactly these files to `$OUT`:

1. **`out/tally.csv`** — header `user,count,tags`, one row per user.
2. **`out/summary.json`** — keys `users` and `events`. One compact JSON object:
   `{"users":3,"events":6}`.

## Messes to expect

- `alice` appears three times with tags login, view, login: sorted, the duplicates stay
- `Hash.new([])` gives every missing key the *same* array and never stores the key — the
  tally then has zero rows
- `Hash.new(0)` is fine for the counter: `0` is immutable, so `+=` replaces the value

## Timebox

Four minutes. A block default that assigns into the hash is the fix; a bare
`Hash.new([])` is the bug.
