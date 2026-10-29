# 183-ruby-encoding-scrub

> "One feed has a lone 0xE9 in the middle of a name. The report must not crash, must not
> guess, and must show the byte counts next to the character counts."

## Input

`in/raw.txt` — **bytes**, one record per line, encoded as UTF-8 **except where the source
was broken**. Line endings are `\n`.

## Rules

For each line report:

1. `valid` — `true` when the line is valid UTF-8, `false` otherwise
2. `bytes` — the raw byte length of the line
3. `chars` — the character length of the **repaired** text
4. `text` — the line with every invalid sequence replaced by `?`

## Output

Write exactly these files to `$OUT`:

1. **`out/lines.csv`** — header `line,valid,chars,bytes,text`, one row per line, in order.
2. **`out/summary.json`** — keys `lines` and `invalid`. One compact JSON object:
   `{"lines":3,"invalid":1}`.

## Messes to expect

- `café` is 4 characters and **5 bytes**: two things, two numbers
- a lone `0xE9` is not a UTF-8 sequence: `valid_encoding?` is false and `scrub("?")` gives
  `caf?`
- `force_encoding("UTF-8")` does not repair anything — it relabels the bytes
- ASCII is valid UTF-8: 2 characters, 2 bytes

## Timebox

Four minutes. Read binary, label, validate, scrub — in that order.
