# 009-jsonl-stream

> "Event feed, one JSON per line. How many per country, and what tags are hot?"

## Task

`in/events.jsonl` is newline-delimited JSON. Each line is one event:

```json
{"id": 1, "user": {"id": "u1", "country": "CA"}, "amount": 12.5, "tags": ["red", "new"]}
```

## Rules

1. Read it as a **stream** — one object per line, never the whole file at once.
2. `country` comes from `user.country`; `amount` is a number.
3. An event with an empty `tags` array contributes nothing to the tag counts.
4. `users` counts **distinct** `user.id` values.

## Output

**`out/by_country.csv`** — header, then one row per country:

```
country,events,revenue
```

Ordered by `revenue` **descending**, ties by `country` ascending. `revenue` is a number.

**`out/tags.csv`** — header, then one row per tag:

```
tag,count
```

Ordered by `count` **descending**, ties by `tag` ascending.

**`out/summary.json`** — exactly two keys: `events` and `users`.

## Messes to expect

- a nested object (`user`) and a nested array (`tags`) in the same record
- an empty array
- two countries with the same revenue

## Timebox

3 minutes. `jq -n 'reduce inputs as ...'` folds the whole file in one pass.
