# 121-openapi-diff

> "Two versions of the users API. Tell me which endpoints moved, and which of those moves
> will break the mobile client that is already shipped. A list of 30 'differences' is
> useless; I need the breaking ones separated out."

## Input

- `in/old.json` — the spec the shipped client was built against.
- `in/new.json` — the spec on the release branch.

Both are OpenAPI-ish documents:

```json
{"openapi": "3.0.0",
 "paths": {
   "/users": {
     "get": {"operationId": "listUsers",
             "parameters": [{"name": "limit", "in": "query", "required": false}],
             "responses": {"200": {"description": "ok"}}}}}}
```

## Rules

1. **An endpoint is a `(path, method)` pair.** The methods are exactly `get`, `put`,
   `post`, `delete`, `patch`, `head`, `options` — lowercase keys under a path object. Any
   other key under a path object (`summary`, `parameters`, `x-internal`, …) is ignored.
   Path keys are compared as literal strings: `/users` and `/users/` are **different**
   paths. A missing `paths` object means no endpoints.
2. **Endpoint sets decide the first two codes:**
   - `removed` — the pair is in `old` and not in `new`.
   - `added` — the pair is in `new` and not in `old`.
3. **For a pair present in both**, compare the operations:
   - `operation-id-changed` — the `operationId` differs. A missing (or `null`)
     `operationId` is the empty string, so `""` -> `metrics` **is** a change.
   - `required-param-added` — the new operation has a required parameter that the old one
     did not have. A parameter is identified by the pair (`name`, `in`); it is required
     when its `required` field is exactly `true` (missing `required`, or `false`, means
     optional). Compare the *sets of required parameters*, so an existing optional
     parameter that becomes required is also `required-param-added`.
   - `param-removed` — a parameter (identified by (`name`, `in`)) that the old operation
     had and the new one does not have. Whether the old one was optional or required does
     not matter for this code.
4. A pair present in both can carry **several** codes, including none.
5. `removed`, `required-param-added` and `operation-id-changed` are **breaking**.
   `added` and `param-removed` are **safe**.

## Output

Write exactly these files to `$OUT`:

1. **`out/changes.csv`** — header `path,method,code`. One row per (endpoint, code). A pair
   that changed in two ways gets two rows. Sorted by `path` ascending, then `method`
   ascending, then `code` ascending — plain byte order (`LC_ALL=C`).
   `code` is exactly one of `removed`, `added`, `operation-id-changed`,
   `required-param-added`, `param-removed`.
2. **`out/summary.json`** — an object with exactly these keys:
   - `endpoints_old`, `endpoints_new` — endpoint counts per document (int)
   - `added`, `removed` — number of rows carrying that code (int)
   - `breaking` — number of rows whose code is breaking (int)
   - `safe` — number of rows whose code is safe (int)
   - `changed_endpoints` — endpoints present in **both** documents that carry at least one
     code (int). An endpoint that only exists on one side is not counted here, even
     though it produced a row.

## Messes to expect

- `/users/` and `/users` are distinct paths, so dropping the trailing-slash variant is a
  `removed` endpoint, not a no-op
- one path keeps its `get` but loses its `delete`, and another keeps `get`/`post` and
  gains a `put`: those are separate codes on separate endpoints
- an operation with no `operationId` at all: it compares as `""`, and gaining one is
  `operation-id-changed`
- a parameter with `"required": true`, a parameter with `"required": false`, and a
  parameter with no `required` key at all — the last two are optional
- an optional parameter that becomes required (`window` on `/metrics`), and a parameter
  whose location changes: `in` is part of the identity, so `/reports` losing `format`
  (`in: query`) while gaining `X-Tenant` (`in: header`) is a removal **plus** an addition,
  not a change to one parameter
- path-level keys (`parameters`, `summary`, `x-internal`) that look like operations but
  are not
- `/users/{id}` and `/users/lookup` sort as literal strings: `l` (0x6c) before `{` (0x7b)

## Timebox

Five minutes. Build a dictionary keyed by (path, method) for each document, then one pass
over the union; if you are looping over documents inside loops over other documents, the
approach is wrong.
