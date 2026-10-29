# 174-perl-unpack-binary

> "The export is a binary blob: a magic header, then records with a length-prefixed name.
> The last record is cut off mid-write and I want it counted, not guessed."

## Input

`in/records.bin` — binary:

- bytes 0–3: the ASCII magic `SRV1`
- then, repeatedly:
  - `N` — record id, unsigned 32-bit **big-endian**
  - `n` — score, unsigned 16-bit big-endian
  - `C` — flags, one byte
  - `C` — name length, one byte
  - `a<len>` — name, `len` bytes, may be empty

## Rules

1. A file that does not start with `SRV1` is a hard error: print the problem and exit
   non-zero. Do not write partial output.
2. Walk the records by offset. A record is complete only when the whole 8-byte fixed part
   **and** the declared name are present.
3. A trailing fragment shorter than a complete record is **truncated**: count it, skip it,
   and do not invent its fields.
4. Report `bytes_read` as the bytes covered by complete records plus the 4-byte magic, and
   `bytes_total` as the file size.

## Output

Write exactly these files to `$OUT`:

1. **`out/records.csv`** — header `id,score,flags,name`, one row per complete record, sorted
   by `id` ascending numerically. Names are plain ASCII and contain no commas.
2. **`out/summary.json`** — an object with exactly these keys:
   - `records` — complete records (int)
   - `truncated` — trailing fragments skipped (0 or 1) (int)
   - `bytes_read` — bytes of complete records plus the magic (int)
   - `bytes_total` — file size in bytes (int)

   One compact JSON object: `{"records":4,"truncated":1,"bytes_read":54,"bytes_total":60}`.

## Messes to expect

- the name may be empty: `name_len` 0 means four empty-field rows, not a missing one
- the trailing fragment has an id and two bytes of score: incomplete, counted, skipped
- scores span 0 to 65535, so a byte-order mistake turns 100 into 25600
- the magic is 4 bytes: a file that is shorter than 4 bytes is a hard error

## Timebox

Five minutes. `unpack("N n C C", substr($data, $offset, 8))`, then check the length prefix
before slicing the name.
