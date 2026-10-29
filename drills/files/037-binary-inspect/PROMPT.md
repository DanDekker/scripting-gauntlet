# 037-binary-inspect

> "A customer sent us a broken export — 111 bytes of junk with no extension, and we
> can't get another copy. Tell me what's inside it: the readable strings, whether it's
> NUL-padded, and whether there's a real file header buried in there somewhere."

## Task

`in/blob.bin` is a raw byte sequence. Walk it byte by byte and report what you find.
Every answer is measured in **byte offsets from the start of the file**, counting from 0.

## Rules

1. **Printable** means `0x20`–`0x7e` inclusive. Nothing else — no tab, no newline, no
   high bytes.
2. A **string** is a maximal run of consecutive printable bytes at least **4** bytes
   long. Runs of 1–3 bytes are not strings.
3. **NUL bytes** are bytes with value `0x00`. Count every one, wherever it is.
4. **Embedded magic**: scan the whole file (not just the start) for the first occurrence
   of any signature, by offset ascending. Report the kind and the offset of its first
   byte. Signatures, in the order they win a tie at the same offset:

   | leading bytes | kind |
   | --- | --- |
   | `89 50 4e 47` | `png` |
   | `1f 8b` | `gzip` |
   | `25 50 44 46` | `pdf` |
   | `50 4b 03 04` | `zip` |
   | `7f 45 4c 46` | `elf` |
   | `ff d8 ff` | `jpeg` |

   If nothing matches, kind is `none` and the offset is `-1`.
5. Byte-exact: no decoding the file as text, no stripping, no normalising.

## Output

**`out/strings.txt`** — one line per string, in ascending offset order, as
`<offset><TAB><text>` (decimal offset, one literal tab, the text).

**`out/report.json`** — exactly five keys:

- `size_bytes` — the file's size
- `nul_bytes` — how many `0x00` bytes
- `string_count` — how many lines you wrote to `strings.txt`
- `embedded_magic` — one of the kinds above, or `none`
- `magic_offset` — offset of the first byte of the signature, or `-1`

## Messes to expect

- NUL padding in front of the first string
- a run of 3 printable bytes that is **not** a string
- a tab inside an otherwise readable line — it splits the run in two
- a file header with no extension and no warning
- high bytes (`0xfe`) sitting next to printable text

## Timebox

3 minutes. `od -An -v -tu1` or `bytes` and one index loop. Do not reach for `strings`:
its minimum length and its idea of printable are not this contract.
