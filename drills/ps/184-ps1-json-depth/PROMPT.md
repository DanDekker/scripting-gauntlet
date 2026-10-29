# 184-ps1-json-depth

> "The service config is four levels deep in places. The exporter printed
> `System.Collections.Hashtable` where the CPU limits should be, and nobody noticed for a
> week."

## Input

`in/config.json` — one nested object.

## Rules

1. Flatten the object to dotted keys:
   - an object contributes `parent.child` keys, recursively
   - `null` is a value: type `null`, empty text
   - an array becomes type `array` with its elements joined by `|`
   - booleans print `true`/`false`, numbers print bare, strings print as-is
2. Also emit the parsed config again as JSON with the **full** structure intact.
3. Sort the flattened rows by key ascending in ordinal (byte) order.

## Output

Write exactly these files to `$OUT`:

1. **`out/flat.csv`** — header `key,type,value`, one row per leaf.
2. **`out/echo.json`** — the config re-serialised, nesting preserved.
3. **`out/summary.json`** — keys `keys`, `nulls`, `arrays`. One compact JSON object:
   `{"keys":7,"nulls":1,"arrays":1}`.

## Messes to expect

- `service.limits.cpu` is an object two levels down: a depth-2 serialiser replaces it with
  a type name
- `note` is `null`: it survives as a leaf, it does not disappear
- `service.tags` is an array of two elements, joined as `a|b`
- `debug` is `false`, which is a value, not an absence

## Timebox

Five minutes. `ConvertTo-Json -Depth 10` for the echo, and walk `.PSObject.Properties` for
the flatten — the default depth is the trap.
