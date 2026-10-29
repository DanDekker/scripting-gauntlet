# 073-http-pagination

> "The item list is paginated and some ids show up twice across page boundaries. Give me
> one clean list, ordered by id, plus how many pages that took."

## Task

Walk the collection at `$API_BASE/items`. The first page is `/items`; each response is
`{"items": [{"id": <int>, "name": <str>}, ...], "next": <cursor or null>}`. Follow `next`
with `?cursor=<cursor>` until it is `null`.

## Rules

1. A non-`200` response is an error: print the URL and status on stderr, exit non-zero.
2. A transport failure, a body whose `items` is not an array of objects, or a `next` that is
   neither a string nor `null` is an error too.
3. Deduplicate by `id`, keeping the **first** occurrence.
4. Stop after 10 pages: a server that never returns `next: null` is broken, so fail loudly.
5. Do not assume the pages arrive in id order or that ids are contiguous.

## Output

- `out/items.csv` - header `id,name`, one row per id, ascending by numeric id.
- `out/summary.json` - exactly three integers: `pages` (responses read), `items` (unique ids
  written), `duplicates` (rows discarded).

## Messes to expect

- an id repeated on two pages with a different name (the first one is the truth)
- pages out of order
- a page with a single item

## Timebox

4 minutes. Loop on `next`, append every row, dedupe once at the end.
