# 101-schema-migrate

> "I renamed a field and tightened a type. Before I ship this, tell me what breaks the
> clients that already consume the old shape — and what is merely additive."

## Input

`in/old_schema.json` and `in/new_schema.json` — JSON-Schema-ish objects:

```json
{
  "type": "object",
  "properties": {"id": {"type": "string"}, "count": {"type": "integer"}},
  "required": ["id"]
}
```

`properties` maps a property name to its definition. `required` is a list of property
names. Both keys may be missing from a file.

## Rules

Only the **top-level** `properties` are compared. A property whose own value is an object
with its own `properties` (a nested object) is compared as an opaque value: changes
inside it are **not** reported.

Two derived sets drive the required-ness codes:

- `old_req` = the names in `old.required` that also exist in `old.properties`
- `new_req` = the names in `new.required` that also exist in `new.properties`

A `required` entry naming a property with no definition is ignored — it is not a property
and it is not a change.

For every property name in `old.properties` ∪ `new.properties`, emit a `(property, code)`
row for each code that applies:

| code | when |
| --- | --- |
| `removed` | the name is in `old.properties` and not in `new.properties` |
| `added` | the name is in `new.properties` and not in `old.properties` |
| `type-changed` | the name is in both and the `type` values differ (a missing `type` compares as the empty string `""`) |
| `now-required` | the name is in both, in `new_req` and not in `old_req` |
| `now-optional` | the name is in both, in `old_req` and not in `new_req` |

- `removed` and `added` are exclusive: a name that exists on only one side gets that one
  code and nothing else (a removed property that was required is `removed`, **not**
  `now-optional`).
- A name present on both sides can carry several codes: `type-changed` and
  `now-required`/`now-optional` are decided independently.

## Output

Write exactly these files to `$OUT`:

1. **`out/changes.csv`** — header `property,code`. One row per `(property, code)` pair,
   sorted by `property` ascending, then `code` ascending (plain string order). `code` is
   exactly one of `removed`, `added`, `type-changed`, `now-required`, `now-optional`.
2. **`out/summary.json`** — an object with exactly these keys:
   - `breaking` — number of rows whose code is `removed`, `type-changed` or
     `now-required` (int)
   - `safe` — number of rows whose code is `added` or `now-optional` (int)
   - `properties` — number of distinct property names appearing in any row (int)

## Messes to expect

- `count` is both `type-changed` (`integer` → `number`) and `now-required`
- `notes` has `{"type": "string"}` in old and no `type` at all in new: that is
  `type-changed` (`"string"` vs `""`)
- `meta` is a nested object: it gained an inner property (`team`), which is **not**
  reported — but `meta` did drop out of `required`, so it is `now-optional`
- `legacy_flag` is gone from `new.properties` while still listed in `old.required`: one
  `removed` row, no `now-optional` row
- `display_name` is new and already required: one `added` row, no `now-required` row
- `ghost` and `old_ghost` are listed in `required` but defined nowhere: ignored

## Timebox

A few minutes. If you are past that, the approach is wrong.
