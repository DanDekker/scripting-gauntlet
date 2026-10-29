# 034-file-type-sniff

> "Someone dumped a folder of exports on me and half the names are wrong — the `.csv`
> won't open in anything. Tell me what these files actually are, before I trust a
> single extension in there."

## Task

`in/` holds ten files. Their extensions are not evidence: one `.csv` is really gzip,
one `.txt` is really a PNG, one `.dat` is really UTF-16. Identify each file by its
**first bytes** and write a report.

## Rules

1. Read the first 8 bytes of each file. `magic` is those bytes as **lowercase hex**, no
   separators, no `0x` (16 hex chars for every file here).
2. `kind` is decided by the leading bytes, checking this table in order:

   | leading bytes | kind |
   | --- | --- |
   | `1f 8b` | `gzip` |
   | `89 50 4e 47` | `png` |
   | `25 50 44 46` | `pdf` |
   | `50 4b 03 04` | `zip` |
   | `7f 45 4c 46` | `elf` |
   | `ff d8 ff` | `jpeg` |
   | `ff fe` | `utf16le` |
   | `ef bb bf` | `utf8bom` |

3. If nothing matches: `ascii` when **every** byte in the file is printable ASCII
   (`0x20`–`0x7e`) or tab (`0x09`), LF (`0x0a`), CR (`0x0d`); otherwise `unknown`.
4. The extension is never consulted. A `.txt` that is a PNG is reported as `png`.

## Output

**`out/types.csv`** — header `filename,kind,magic`, one row per file in `in/`, sorted by
`filename` ascending (byte order). `filename` is the basename, no directory.

**`out/summary.json`** — exactly three keys:

- `files` — how many files were reported
- `kinds` — how many **distinct** `kind` values appear
- `text_files` — how many files have kind `ascii`, `utf8bom` or `utf16le` (the ones you
  could actually read as text)

## Messes to expect

- a gzip stream named `.csv`
- a PNG named `.txt`
- a UTF-16 BOM that would decode as garbage if you assumed UTF-8
- a file with no recognisable magic at all — it is not necessarily text
- a text file whose first 8 bytes look like `id,name,`

## Timebox

3 minutes. `head -c 8 | od -An -tx1` or `read_bytes()[:8].hex()`, a `case`/dict, done.
