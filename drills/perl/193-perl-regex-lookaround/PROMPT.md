# 193-perl-regex-lookaround

> "Audit logs contain transaction amounts embedded in free text, as well as recurring sensor
> telemetry motifs. Consuming regexes miss overlapping motifs and capture false positives
> inside variable names like `TEST_USD999`."

## Input

`in/stream.txt` — mixed transaction and telemetry records:

```
AUDIT101: approved USD150 and EUR40
AUDIT102: skip TEST_USD999 and EUR100x and USD
AUDIT103: approved GBP300 and USD250
MOTIF104: target=ABA seq=ABABA
MOTIF105: target=XAX seq=XAXAXAX
```

Blank lines and `#` comments are skipped.

## Rules

1. On lines starting with `AUDIT<id>`:
   Extract valid currency amounts:
   - Currency code is `USD`, `EUR`, or `GBP`
   - Must **not** be preceded by word character: `(?<!\w)`
   - Must be followed immediately by integer digits `\d+`
   - Must be followed by word boundary, whitespace, punctuation, or end of string: `(?=[,\s\.]|$)`
   Record: `id = AUDIT<id>`, `type = currency`, `key = <currency>`, `val = <amount>`.
2. On lines starting with `MOTIF<id>`:
   Parse `target` and `seq` (e.g. `target=ABA seq=ABABA`):
   - Capture **overlapping** occurrences of `target` in `seq` using zero-width lookahead: `(?=(\Q$target\E))`
   - In `ABABA`, both `ABA` at offset 1 and `ABA` at offset 3 must be captured.
   - In `XAXAXAX`, `XAX` at offsets 1, 3, 5 must be captured.
   Record: `id = MOTIF<id>`, `type = motif`, `key = <target>`, `val = <1-based offset>`.

## Output

Write exactly these files to `$OUT`:

1. **`out/extractions.csv`** — header `id,type,key,val`.
2. **`out/summary.json`** — keys `records`, `currencies`, `motifs`. One compact JSON object:
   `{"records":9,"currencies":4,"motifs":5}`.

## Messes to expect

- `TEST_USD999` must not match because of preceding `_`.
- `EUR100x` must not match because of trailing `x`.
- Standard `/ABA/g` matches once in `ABABA`; lookahead `/(?=(ABA))/g` is required to capture the overlap.

## Timebox

Four minutes. Use `(?<!\w)` for currency and `(?=(...))` for overlapping motifs.
