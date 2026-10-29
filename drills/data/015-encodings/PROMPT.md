# 015-encodings

> "Five exports from five different systems. Same three columns. Give me one file."

## Task

`in/` holds five CSV files that all have the same shape (`id,name,city`) but were
produced by different systems:

| file | quirk |
| --- | --- |
| `utf8.csv` | plain UTF-8 |
| `utf8bom.csv` | UTF-8 with a byte order mark |
| `utf16le.csv` | UTF-16 little endian |
| `latin1.csv` | latin-1, so `é` is one byte, not two |
| `crlf.csv` | Windows line endings |

All five are valid data. Decode each one, strip the BOM if present, normalise line
endings to `\n`, and merge them.

## Rules

1. Output is **UTF-8** with `\n` line endings. Non-ASCII characters must survive
   intact — `Zoë` is not `Zo?`.
2. A byte order mark is **not** part of the first field.
3. `latin1.csv` is not valid UTF-8. Decoding it as UTF-8 must not silently corrupt it.
4. Add a `source` column holding the file's name **without** the `.csv` extension.
5. Sort rows by `id` **ascending** (numeric).

## Output

**`out/merged.csv`** — header, then the rows:

```
id,source,name,city
1,utf8,Zoë,Montréal
```

**`out/summary.json`** — exactly two keys: `files` (how many files were read) and `rows`.

## Messes to expect

- a BOM that silently becomes part of the first `id`
- `latin1.csv` failing to decode as UTF-8
- `\r` left at the end of the last field

## Timebox

5 minutes. `iconv` and a byte-order-mark check are enough; python needs
`bytes.decode` with a fallback.
