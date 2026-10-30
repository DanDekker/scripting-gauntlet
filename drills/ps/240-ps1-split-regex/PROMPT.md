# 240-ps1-split-regex

> "A build feed is four pipe-delimited columns. The parser splits on `|`, and every row
> comes back as a hundred characters instead of four fields. The version split is worse:
> `1.10.2` yields nothing at all."

## Input

`in/builds.log` — pipe-delimited rows, `pkg|version|sha|size`:

```
# pkg|version|sha|size
web|1.10.2|a3f9c1d|20480
api|2.0.11|9be7f02|40960

web|1.9.14|c0ffee1|1024
cli|0.4.0|deadb3e|512
ops|1.0|tooshort|  12  
```

Blank lines and lines starting with `#` are skipped. Each field is trimmed of
surrounding whitespace before use.

## Rules

1. Split each row into **exactly four** fields. The separator is a literal pipe.
2. `version` must be `major.minor.patch` — three numeric components separated by a
   literal dot. Any other shape is **malformed**.
3. `size` must be all digits. Any other shape is **malformed**.
4. A malformed row is counted and skipped: it produces no output row.
5. Keep input order.

## Output

Write exactly these files to `$OUT`:

1. **`out/builds.csv`** — header `pkg,major,minor,patch,sha,size`, one row per accepted
   record, `major`/`minor`/`patch`/`size` as integers.
2. **`out/summary.json`** — keys `rows`, `malformed`, `total_size`, `packages` (distinct
   package names, ordinal). One compact JSON object:
   `{"rows":4,"malformed":1,"total_size":62976,"packages":3}`.

## Messes to expect

- `-split '|'` is an empty-alternation regex: it splits between every character.
- `-split '.'` is the any-character class: six empty fields, and `[int]''` throws.
- `'a+b*c' -split '+'` does not merely mis-split — it throws.
- `1.0` is a two-part version, so the `ops` row is malformed, not a row with an empty patch.
- `  12  ` needs trimming before the digits check.

## Timebox

Five minutes. `-split '\\|'` and `-split '\\.'`, or `.Split('|')` / `.Split('.')`.
