# 035-split-merge

> "The upload endpoint dies on anything over a few megs, so I ship it in five-row
> pieces and glue it back together on the far side. Prove the glue works before I
> trust it with a real export."

## Task

Split `in/events.csv` into chunks of **5 data rows**, then merge the chunks back and
prove the reassembly is byte-identical to the original.

## Rules

1. Every chunk file starts with the header row, then **at most 5 data rows**, in the
   original order.
2. The last chunk holds the remainder (1 to 5 rows). Never pad it, never write an empty
   chunk, never leave the remainder on its own.
3. Chunks are named `chunk_01.csv`, `chunk_02.csv`, ... — 1-based, zero-padded to two
   digits, in file order.
4. Fields are copied verbatim. Quoted fields stay quoted, nothing is re-ordered,
   re-quoted or re-formatted.
5. `merged.csv` is the header once, then every chunk's data rows in chunk order. It must
   be **byte-identical** to `in/events.csv` — same bytes, same trailing newline. If it is
   not, print what differs and exit non-zero.

## Output

- `out/chunk_01.csv` ... `out/chunk_05.csv` — the chunks.
- `out/merged.csv` — the reassembled file.
- `out/report.json` — exactly four keys: `rows` (data rows in the input, header
  excluded), `chunk_size` (5), `chunks` (how many chunk files you wrote), `roundtrip`
  (`true` only if `merged.csv` matched the original byte for byte).

## Messes to expect

- 23 data rows, so the last chunk is short and there are 5 chunks, not 4
- fields containing commas, wrapped in quotes
- a field with spaces in it (`report.csv 42 rows`)
- CRLF would break `cmp`, but this file is LF-only

## Timebox

3 minutes. One awk pass that writes chunk files, then `cat` and `cmp`.
