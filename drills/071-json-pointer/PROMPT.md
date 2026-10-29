# 071-json-pointer

> "I have a big API response and a list of the paths I care about. Pull those values out
> and leave a blank where the path does not exist."

## Task

`in/paths.txt` holds one JSON Pointer (RFC 6901) per line. For each pointer, resolve it
against `in/doc.json`.

## Rules

1. Skip blank lines and lines beginning with `#`.
2. Every pointer starts with `/`; otherwise print the line and exit non-zero.
3. Split on `/` first, then unescape each token: `~1` becomes `/`, then `~0` becomes `~`.
   That order matters: `~01` is the literal `~1`.
4. Walk the document token by token. On an object a token is a key. On an array the token
   must be a non-negative integer without leading zeros; use it as an index.
5. A missing key, an index out of range, or walking into a scalar is a **miss**, not an error.
6. Report scalars only: strings verbatim, numbers in their plain form (`1`, `3.5`),
   `true`/`false` as written. `null`, objects and arrays are blank cells.

## Output

- `out/values.csv` - header `path,value`, one row per pointer in input order, the pointer
  copied exactly as written.
- `out/summary.json` - exactly three integers: `paths` (pointers examined), `found`,
  `missing`.

## Messes to expect

- `~1` and `~0` escapes, including a key that contains a `/`
- an array index past the end of an empty array
- a key with a space in it, a `null` value, and an empty object

## Timebox

3 minutes. Unescape after splitting, and let one resolver handle both dicts and lists.
