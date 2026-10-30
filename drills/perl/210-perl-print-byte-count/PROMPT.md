# 210-perl-print-byte-count

> "The nightly report claimed it was 4 bytes long. It had written 26. The size came
> from `my $bytes += print $fh $item;` — and `print` returns **1** for every successful
> call, so the 'size' was really the number of items."

## Input

`in/items.txt` — one item per line, UTF-8:

```text
alpha
bravo
charlie
café
```

## Rules

1. Read `in/items.txt`, one item per line.
2. Write **`out/report.txt`** — each item on its own line, in input order, exactly as it
   appears in the input, each line ending with a newline.
3. **`out/summary.json`** — keys `items`, `bytes`. One compact JSON object.
   - `items` — the number of items.
   - `bytes` — the number of **bytes** in `out/report.txt`, including the newline that
     ends each line. The file is UTF-8: `café` is 4 characters but 5 bytes.

## Messes to expect

- `print` returns **1** when it succeeds. It does not return the number of characters
  written, so adding up the return values gives you the number of calls.
- Measure the bytes instead: the length of the text you wrote, or the size of the file
  on disk after you close it. Text read from a file without decoding counts bytes.

## Timebox

Four minutes.
