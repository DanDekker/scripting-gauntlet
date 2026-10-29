# 094-agent-trace

> "Here is the raw JSONL trace from that agent run. How many turns did it take, what did
> it cost me in tokens, and which tool did it lean on?"

## Input

`in/trace.jsonl` — one JSON object per line, for example:

```json
{"turn":1,"tool":"read_file","tokens":1200,"cached":false,"error":null}
```

Fields: `turn` (int), `tool` (string), `tokens` (int), `cached` (bool), `error` (string or
null).

The file is messy: blank lines, a line that is not JSON at all, trailing whitespace, one
record with no `tool` key, records with `"cached": true`, and records whose `error` is a
string such as `"timeout"`.

## Rules

1. **Survive the junk.** Skip blank lines, any line that is not valid JSON, any line that
   is valid JSON but not an object, and any object without a `tool` key. Never abort on a
   bad line. Every record that survives is a **turn**.
2. **Billed vs cached.** A record with `"cached": true` did not cost tokens: its `tokens`
   go to `cached_tokens` and **not** to `total_tokens`. Every other record's `tokens` are
   billed and count toward `total_tokens`. A missing `tokens` field counts as `0`.
3. **Error turn.** A record is an error turn when it has an `error` key whose value is not
   `null` (any string counts, including `""`). Records with `"error": null` or no `error`
   key are not error turns.

## Output

Write exactly these files to `$OUT`:

1. **`out/tools.csv`** — header `tool,calls,errors,tokens`. One row per distinct `tool`,
   sorted by `tool` ascending in byte order (case-sensitive).
   - `calls` — records for that tool, cached or not (int)
   - `errors` — error turns for that tool (int)
   - `tokens` — **billed** tokens for that tool only: cached records contribute 0 (int)
2. **`out/summary.json`** — an object with exactly these keys:
   - `turns` — surviving records (int)
   - `total_tokens` — billed tokens over all tools (int)
   - `cached_tokens` — tokens from cached records (int)
   - `error_turns` — error turns over all tools (int)
   - `most_called_tool` — the tool with the most calls (string); ties go to the
     alphabetically first tool name; `""` if there are no records

## Messes to expect

- the invalid-JSON line and the `tool`-less record are not turns: they must not appear in
  `turns`, `tools.csv`, or any sum
- `read_file` has 2 calls but only 1 billed: its cached record must not inflate `tokens`
- `grep` is called 3 times, twice billed — the highest call count, so it is
  `most_called_tool`
- a cached record can still be an error turn; `calls`, `errors` and `tokens` are three
  independent columns

## Timebox

A few minutes. If you are past that, the approach is wrong.
