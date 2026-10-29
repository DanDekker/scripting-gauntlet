# 003-http-probe

> "Before I wire this into anything, poke the API and tell me what's actually there.
> It's paginated. And it's a local stub, so nothing can break."

## Task

A service is listening at `$API_BASE`. Probe it and collect everything it has.

## Endpoints

- `GET /health` → `{"ok": true, "version": "2.3.1"}`
- `GET /api/v1/items?page=N` → `{"items": [...], "next": "/api/v1/items?page=N+1"}`

`next` is `null` on the last page. **Follow the `next` link** — do not assume how many
pages there are, and do not build the next URL from the page number.

## Rules

1. Hit `/health` first. If `ok` is not `true`, print why and exit non-zero — do not
   continue against a service that says it is unhealthy.
2. Page until `next` is `null`, collecting every item.
3. **Cap the loop** (50 pages is plenty). If a page returns a `next` you have already
   visited, or the cap is hit, fail loudly. A pagination bug must not hang the job.
4. Sort the collected items by `id` before writing.

## Output

**`out/items.json`** — a JSON array of every item, sorted by `id` ascending:

```json
[{"id": 1, "name": "item-01"}, ...]
```

**`out/report.json`** — exactly these four keys:

```json
{"ok": true, "version": "2.3.1", "item_count": 12, "pages": 3}
```

`pages` is how many item pages you actually fetched.

## Messes to expect

- the last page is short, and `next` there is `null` rather than missing
- the item list is not sorted by the server
- a `next` value that is a path, not an absolute URL

## Timebox

3 minutes. `curl` + `jq` in a `while` loop, or fifteen lines of python.
