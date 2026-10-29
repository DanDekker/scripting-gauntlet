# 142-function-call-repair

> "Our agent logs the tool calls the model wanted to make, but half the `raw_args` are
> not JSON — Python quotes, trailing commas, `True`/`None`, sometimes the braces are just
> missing. Fix what can be fixed mechanically, tell me exactly what you fixed, and do not
> invent arguments for the ones you cannot."

## Input

`in/calls.jsonl` — one JSON object per line:

```json
{"call_id": "c1", "name": "search", "raw_args": "{\"query\": \"hello\"}"}
```

- `call_id` — the call identifier (string)
- `name` — the tool name (string)
- `raw_args` — the model's argument text, **as a string**, which may or may not be JSON

## Rules

### Which lines are calls

A line is processed only when it parses as a JSON **object** and has all three keys
`call_id`, `name`, `raw_args`. Blank lines, lines that are not valid JSON, lines that are
valid JSON but not an object (e.g. `[1, 2]`), and objects missing any of the three keys
are skipped and counted nowhere. Processed calls keep **input order**.

### Parsing `raw_args`

1. Trim surrounding whitespace from `raw_args`.
2. If it parses as JSON **and** the value is an object or an array, the call is `valid`.
3. Otherwise apply these repairs, **in this order**:
   1. **Wrap** — if the trimmed text does not start with `{` or `[`, wrap it in `{` and
      `}`. (Empty text therefore becomes `{}`.)
   2. **Python literals** — outside single- or double-quoted regions, replace the whole
      words `True` -> `true`, `False` -> `false`, `None` -> `null`. A word means the
      characters around it are not `[A-Za-z0-9_]`.
   3. **Single quotes** — outside double-quoted regions, replace each `'` with `"`.
      (Backslash escapes inside a double-quoted region are copied untouched.)
   4. **Trailing commas** — delete a `,` that is followed only by spaces, tabs, CR or LF
      and then `}` or `]` (the regex `,([ \t\r\n]*[}\]])` -> `\1`). A comma inside a
      string is left alone unless the same pattern applies there.
4. Parse the repaired text. If it parses as an object or array: `repaired`. If it still
   fails, or parses to a scalar: `unfixable`. The four rules above are the whole repair
   vocabulary — an unquoted value such as `{"status": active}` is **not** repaired, it is
   `unfixable`.

## Output

Write exactly these files to `$OUT`:

1. **`out/repaired.jsonl`** — one line per `valid` or `repaired` call, in input order:
   `{"call_id": "<id>", "name": "<name>", "status": "valid|repaired", "args": <parsed>}`.
   Write it compactly: no spaces after `:` or `,`, keys in the order `call_id`, `name`,
   `status`, `args`, and object keys inside `args` sorted ascending (recursively). Integer
   values stay integers. `unfixable` calls do **not** appear here.
2. **`out/report.csv`** — header `call_id,name,status`. One row per processed call, in
   input order, `status` being `valid`, `repaired` or `unfixable`.
3. **`out/summary.json`** — object with exactly these keys:
   - `total_calls` — processed calls (int)
   - `valid_count` — int
   - `repaired_count` — int
   - `unfixable_count` — int

## Messes to expect

- `c1` and `c12` are already valid (padding whitespace is not a defect) and are reported
  `valid`, not `repaired`
- `c2` sets the pattern: `{'path': 'foo.py', 'line': 3}` is one repair, not a rewrite
- `c3`, `c10`, `c13` are trailing commas; `c4`, `c11` are Python literals; `c5` has no
  outer braces
- `c6` (`{"status": active}`) has an unquoted value that no rule covers -> `unfixable`
- `c8` is truncated and cannot be closed -> `unfixable`
- `[1, 2]` on its own line is JSON but not a call, and `c9` is not JSON at all — both are
  skipped, so `total_calls` is smaller than the number of lines
- `c7` parses to an **array**, which is a legal `args` value

## Timebox

About four minutes. If you are past that, the approach is wrong.
