# 146-context-compression

> "This session is 4k tokens of file dumps and it is about to blow the context window.
> Turn it into something I can reload later: keep what was said, keep the shape of what
> was read, and tell me how much we actually saved."

## Input

`in/transcript.jsonl` — one chat message per line:

```json
{"idx": 1, "role": "user", "content": "Please inspect the error in src/main.py and fix it."}
{"idx": 2, "role": "tool", "tool": "read_file", "output": "line 1: import os\nline 2: ..."}
{"idx": 3, "role": "assistant", "content": "I found the issue on line 42: missing comma."}
{"idx": 4, "role": "tool", "tool": "edit_file", "output": "Successfully replaced 1 occurrence."}
```

Roles seen: `user`, `assistant`, `tool`, `system`. Tool messages carry a `tool` name and
an `output` string; the other roles carry a `content` string.

## Rules

### 1. Which lines are messages

Skip a line — counting it nowhere — when it is blank, not valid JSON, valid JSON that is
not an object, an object whose `idx` is missing or is not an integer (a number with a
fractional part is not an integer, and neither is a string), or an object whose `role` is
missing or not a string. Every other line is one **message**.

### 2. Order

Sort the messages by `idx` ascending. Where two messages share an `idx`, keep their input
order. Every list below uses this sorted order — not the order the lines appear in the
file.

A missing or non-string `content` / `output` is the empty string `""`. A missing or
non-string `tool` is the empty string `""`.

### 3. What is kept

- `role` of `user`, `assistant` or `system`: the message is kept **verbatim**. Its text is
  its `content`.
- `role` of `tool`: its text is its `output`, compressed by the tool name:

| tool | compressed text |
| --- | --- |
| `read_file` | `[READ: <n> lines, <c> chars]` |
| `edit_file` | `[EDIT: ok]` when the output contains `Successfully`, else `[EDIT: failed]` |
| `bash` | output longer than 100 chars: first 50 chars + `...[truncated]...` + last 50 chars |
| anything else (including no `tool`) | output longer than 100 chars: first 100 chars + `...` |

For `bash` and the catch-all, an output of **exactly 100 chars is not truncated** — the
test is `> 100`.

`<n> lines` is the number of lines in the original output: split on `\n`, and a single
trailing newline does not add an empty last line. Empty output is `0` lines.

`<c> chars` is the length of the original output in characters (Unicode code points), not
bytes.

### 4. How much was saved

Count characters over the message text only — `content` for user/assistant/system,
compressed `output` for tools:

- `original_chars` — sum of the **uncompressed** lengths
- `compressed_chars` — sum of the **compressed** lengths
- `saved_chars` — `original_chars - compressed_chars`
- `compression_ratio` — `compressed_chars / original_chars`, rounded to 4 decimals;
  `0.0` when `original_chars` is 0

## Output

Write exactly these files to `$OUT`:

1. **`out/compressed.jsonl`** — one compact JSON object per message, one per line, in the
   sorted order of rule 2. No spaces after `:` or `,` (compact separators). Keys, in this
   exact order:
   - non-tool roles: `{"idx":1,"role":"user","content":"..."}`
   - tool messages: `{"idx":2,"role":"tool","tool":"read_file","output":"[READ: ...]"}`
2. **`out/summary.json`** — an object with exactly these keys:
   - `total_messages` — messages that survived rule 1 (int)
   - `tool_messages` — messages whose `role` is `tool` (int)
   - `original_chars` — int
   - `compressed_chars` — int
   - `saved_chars` — int
   - `compression_ratio` — float, 4 decimals

## Messes to expect

- the blank line, `not json`, the JSON array, the message with no `idx`, the message whose
  `idx` is the string `"16"`, and the message with no `role` are **not** messages: the 18
  non-blank lines (`transcript.jsonl` has 20 lines, two of them blank) produce 13 messages
- `idx` values are shuffled in the file; the output starts at `idx` 1, not at the first
  line
- `idx` 10 is a `read_file` with no `output` at all: it still appears, as
  `[READ: 0 lines, 0 chars]`
- `idx` 11 is a `user` message with no `content`: it appears with `"content":""`
- `idx` 12 is a `system` message: kept verbatim, like a human turn
- `idx` 7 is 2 chars of bash output and `idx` 13 is exactly 100 chars: neither is
  truncated, and `idx` 6 is the one that gets `...[truncated]...`
- `idx` 2, 3 are consecutive tool outputs, and so are `idx` 6, 7: consecutive tool
  messages compress independently, they are not merged

## Timebox

Five minutes. If you are past that, the approach is wrong.
