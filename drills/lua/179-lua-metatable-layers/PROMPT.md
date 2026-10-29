# 179-lua-metatable-layers

> "Three config layers, each overriding the one before it. When a value shows up I need to
> know which layer actually set it, and whether this layer owns it or inherited it."

## Input

- `in/layers.txt` — layers in order, each introduced by `layer <name>`, then
  `key=value` lines belonging to that layer
- `in/lookups.txt` — one lookup per line: `<layer> <key>`

```
layer base
region=eu
layer mid
retries=5
```

## Rules

1. Each layer is a table; layer *i* inherits from layer *i-1* through `__index`. The first
   layer has no parent.
2. Resolve a lookup through the chain: the first layer that has the key **itself** wins.
3. Report `value`, the `source` layer name, and `own` — `true` when the queried layer is
   the source, `false` when the value was inherited.
4. A key no layer defines is `absent`: empty value, source `absent`, `own` false.
5. `own_keys` lists the keys each layer holds **itself** (not inherited), sorted, joined
   with `;`.

## Output

Write exactly these files to `$OUT`:

1. **`out/lookups.csv`** — header `layer,key,value,source,own`, one row per lookup in input
   order.
2. **`out/own_keys.csv`** — header `layer,keys`, one row per layer, sorted by layer; `keys`
   is semicolon-joined.
3. **`out/summary.json`** — keys `layers`, `lookups`, `resolved`, `absent`. One compact
   JSON object: `{"layers":3,"lookups":8,"resolved":6,"absent":2}`.

## Messes to expect

- `leaf retries` resolves to `5` from `mid`, but `rawget(leaf, "retries")` is `nil`
- `leaf region` falls through two layers to `base`
- `pairs` on `leaf` sees only `name`: inheritance is not enumeration
- `base tier` is absent even though `mid` defines `tier`: inheritance runs one way

## Timebox

Five minutes. Walk the `__index` chain with `rawget` at each step — that is what gives you
provenance.
