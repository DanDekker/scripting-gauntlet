# 137-sse-parser

> "I captured the raw body of a streaming `/chat/completions` call and I need the answer
> text back out of it - plus enough of a summary to tell whether the capture is complete
> or the stream died half way through."

## Input

`in/stream.txt` - a raw SSE response body, exactly as it came off the socket.

The event payloads are OpenAI-compatible chat chunks:

```json
{"id":"chatcmpl-1","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}
```

## Rules

1. **Frame first.** Strip trailing whitespace (spaces, tabs, and the `\r` of a CRLF
   capture) from every line. After that, a line that is empty **ends the current event**,
   and a run of blank lines ends exactly one event. A trailing block with no closing blank
   line still counts as an event.
2. **Count every event block** in `total_events`, including blocks that carry only comments
   or only `event:`/`id:` fields.
3. A line starting with `:` is a comment. It contributes nothing to the payload but is
   counted in `comment_lines`.
4. Any other line is `field: value`. Drop **one** leading space from the value if there is
   one. Only the `data` field matters; `event:` and `id:` are ignored.
5. **Payload.** An event's payload is its `data` values joined with `\n` (a single `data`
   field is just that value). An event with no `data` field has no payload and is neither a
   chunk nor malformed.
6. If the payload is exactly `[DONE]`, the stream completed normally: set
   `completed_done` to `true`. `[DONE]` is **not** JSON and never counts as malformed.
7. Otherwise parse the payload as JSON. If that fails, the event is a **malformed chunk**:
   increment `malformed_chunks` and skip it.
8. A parsed JSON object with a **non-empty** `choices` array is a **valid chunk**
   (`valid_chunks`, one row of `chunks.csv`, 1-based `chunk_index`). An object whose
   `choices` is missing or `[]` is neither valid nor malformed - it is the usage-only
   tail chunk in this capture.
9. **Content.** `choices[0].delta.content`, when it is a string, is appended to the
   reconstructed message in arrival order. Anything else (missing, `null`, non-string)
   contributes nothing and has `delta_len` 0.
10. **Usage.** If a parsed object has a `usage` object, take `prompt_tokens` and
    `completion_tokens` from it (missing -> 0). If several chunks carry usage, the last
    one wins.

## Output

Write exactly these files to `$OUT`:

1. **`out/message.txt`** - the concatenated content deltas, in arrival order, with no
   separator added between them. If the message is non-empty the file ends with exactly
   one `\n`; if it is empty the file is empty (0 bytes).
2. **`out/chunks.csv`** - header `chunk_index,delta_len,role`, one row per valid chunk in
   arrival order. `delta_len` is the character length of `delta.content` (0 when there is
   none). `role` is `delta.role` when it is a string, otherwise empty.
3. **`out/summary.json`** - an object with exactly these keys:
   - `total_events` (int) - event blocks
   - `comment_lines` (int) - lines starting with `:`
   - `valid_chunks` (int)
   - `malformed_chunks` (int)
   - `total_chars` (int) - characters in the reconstructed message, **not** counting the
     final newline that `message.txt` adds
   - `completed_done` (bool) - `[DONE]` was seen
   - `prompt_tokens` (int)
   - `completion_tokens` (int)

## Messes to expect

- comment lines (`: keepalive ping`) sit between chunks and must not break framing
- one event is a comment line plus an ignored `id:` field: it counts in `total_events` but
  produces no chunk
- one chunk is pretty-printed across two `data:` lines; joined with `\n` it is still valid
  JSON, so it is one chunk, not two
- one `data:` has no space after the colon (`data:{...}`) - the space is optional
- one `data:` line is truncated JSON: malformed, counted, and skipped
- the usage chunk has `choices: []`, so it is not a chunk even though it is valid JSON
- one line ends with a `\r` and one with trailing spaces: both are trailing whitespace
- `delta.content` may be `null` or the whole `delta` may be `{}` - both give `delta_len` 0
- one content delta contains an escaped newline, so the message itself spans two lines

## Timebox

Four minutes. If you are past that, the approach is wrong.
