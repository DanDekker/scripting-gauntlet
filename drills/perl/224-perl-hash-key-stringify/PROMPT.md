# 224-perl-hash-key-stringify

> "The stock lookup missed `007` and `1.0` even though both were in the inventory. The
> lookup code coerced the key to a number first — `0 + $key` — and a hash key is a
> **string**: `007` becomes `7` and `1.0` becomes `1`, so neither matches the key the
> inventory was filed under."

## Input

`in/inventory.txt` — one item per line, `<key> <name>`:

```text
08080 widgets
8080 gadgets
1.0 small
007 bolts
```

`in/lookups.txt` — one key per line, in the order they are looked up:

```text
8080
8079
007
1.0
```

## Rules

1. Read `in/inventory.txt` into a lookup table: the key is the text before the first
   space, the name is the rest of the line.
2. Read `in/lookups.txt`, one key per line, in order.
3. For each lookup, find the inventory entry whose key is **exactly the characters of
   the lookup** — the same text, with no numeric conversion of any kind.
   - `hit` when such an entry exists, and report its name;
   - `miss` when it does not.
4. **`out/lookups.csv`** — header `index,lookup,status,name`. One row per lookup, in
   file order, `index` starting at 1. `name` is empty for a `miss`.
5. **`out/summary.json`** — keys `lookups`, `hits`, `misses`. One compact JSON object.

## Messes to expect

- A hash key is a **string**. `$h{8080}` and `$h{"8080"}` are the same entry, but
  `$h{"08080"}` is not the same entry as `$h{8080}`, and `$h{1.0}` is the key `"1"`
  while `$h{"1.0"}` is the key `"1.0"`.
- `0 + $key` (or `$key + 0`) turns `007` into `7` and `1.0` into `1`, so the lookup
  goes to a key the inventory was never filed under.
- Look the key up as the text you read.

## Timebox

Four minutes.
