# 021-unicode-normalize

> "The CRM has the same person five ways. Build me a match key I can join on."

## Task

`in/names.csv` has `id,raw` — names typed by hand and by three imports.

## Rules

Apply these transformations, in this order:

1. **NFC**-normalise the string (canonical composition). A decomposed `e` + combining acute
   and a precomposed `é` are then the same text.
2. **Casefold**, not `lower`. Casefold is the aggressive form: `ß` becomes `ss`, so
   `Straße` and `STRASSE` both land on `strasse`. `lower` would leave `ß` alone — do not
   use it.
3. **Strip accents**: decompose to NFD, drop every combining mark (`Mn`), recompose to NFC.
   `Café` becomes `cafe`; `İstanbul` becomes `istanbul`.
4. **Collapse whitespace**: every run of spaces/tabs becomes one space, and leading and
   trailing whitespace is removed.

Nothing else changes: characters outside the Latin-accent set survive as they are.

## Output

**`out/normalised.csv`** — header `id,key`, one row per input row in input order.

**`out/summary.json`** — exactly two keys: `rows` (data rows read) and `distinct`
(how many different keys the rows produced).

## Messes to expect

- `Café` precomposed and `Cafe` + combining acute, both meant to be the same
- `Straße` next to `STRASSE`
- `José   Álvarez` with a run of spaces and `JOSE ALVAREZ` next to it
- `İstanbul`, whose casefold adds a combining dot
- padding spaces around some values

## Timebox

3 minutes in python (`unicodedata`); half an hour of pain in awk, so use sed for the
Unicode and let `tr` do ASCII case.
