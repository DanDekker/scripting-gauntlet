# 168-ruby-truthiness

> "Ops flipped debug off, zeroed the retries and emptied the label. The merged config came
> back with debug on and the old label. The defaults ate the overrides."

## Input

Two JSON objects:

- `in/base.json` — the defaults
- `in/override.json` — the environment overrides

Values may be `true`, `false`, `null`, an integer, or a string.

## Rules

1. Start from every key in `base.json`.
2. For every key in `override.json`:
   - if its value is `null`, the key is **removed** from the result (a tombstone), even if
     the base had it;
   - otherwise the override value replaces the base value — including `false`, `0` and
     `""`.
3. A key absent from the override keeps its base value.
4. Sort the result by key ascending in byte order.

## Output

Write exactly these files to `$OUT`:

1. **`out/merged.csv`** — header `key,type,value`, one row per surviving key. `type` is
   `bool`, `int`, `float`, or `string`. `bool` values print as `true` or `false`; an empty
   string prints as an empty field.
2. **`out/summary.json`** — an object with exactly these keys:
   - `keys` — surviving keys (int)
   - `from_override` — surviving keys whose value came from the override (int)
   - `removed` — override keys that were `null` (int)

   Print it as one compact JSON object: `{"keys":5,"from_override":4,"removed":1}`.

## Messes to expect

- `debug` is overridden to `false`: `override[k] || base[k]` would keep `true`
- `cache` is overridden to `null`: it must disappear, not fall back to the base value
- `label` is overridden to `""`: an empty string is truthy in Ruby and must survive
- `retries` is overridden to `0`: zero is truthy in Ruby, but code ported from another
  language often tests it as false

## Timebox

Three minutes. Test presence with `key?`, not truthiness.
