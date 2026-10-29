# 167-ruby-hash-identity

> "The same customer shows up as 1, 1.0 and sometimes '1'. Two of those are one person.
> The third is a different record entirely."

## Input

`in/events.jsonl` — one JSON object per line, each with an `id` and an `action`:

```
{"id": 1, "action": "login"}
{"id": 1.0, "action": "view"}
{"id": "1", "action": "login"}
```

## Rules

1. Skip a blank line.
2. An entry with a `null` id or **no** id key at all is **invalid**: count it and skip it.
3. An id that is a JSON number is **numeric**; an id that is a JSON string is a
   **string**. The two are different entities and are reported separately.
4. Numeric ids that are numerically equal are the same entity: `1` and `1.0` merge. A
   numeric id is printed as its integer form, so `1.0` prints as `1`.
5. Count events per `(id, kind)` pair.

## Output

Write exactly these files to `$OUT`:

1. **`out/tally.csv`** — header `id,kind,events`, one row per pair, where `kind` is
   `numeric` or `string`. Sort by `id` ascending in byte order, then by `kind` ascending.
2. **`out/summary.json`** — an object with exactly these keys:
   - `ids` — rows in `tally.csv` (int)
   - `events` — accepted entries (int)
   - `invalid` — entries with a null or absent id (int)

   Print it as one compact JSON object: `{"ids":4,"events":8,"invalid":2}`.

## Messes to expect

- `1` and `1.0` must land in the same row — a plain Hash will keep them apart
- `"1"` is a separate row from `1`, and both print an `id` of `1`
- one entry has `"id": null` and one has no `id` key: both are invalid
- `"2"` and `2` are likewise two rows

## Timebox

Three minutes. Normalize the key before you count: `(kind, text)`, not the raw value.
