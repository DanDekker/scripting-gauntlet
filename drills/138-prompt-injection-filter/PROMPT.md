# 138-prompt-injection-filter

> "We pipe user messages and tool output into the same context window, so both are
> untrusted. Give me a per-record verdict I can gate on, and tell me which patterns the
> corpus actually hits so I know what to arm."

## Input

`in/inputs.jsonl` - one JSON object per line:

```json
{"id": "msg-001", "source": "user", "text": "Can you summarize this article?"}
```

- `id` - record identifier (string)
- `source` - `user` or `tool`; may be missing or `null`, which is emitted as the empty string
- `text` - the untrusted text

## Rules

1. **Skip junk.** Blank lines, lines that are not valid JSON, and lines that are valid JSON
   but not an object are skipped and **not counted anywhere**. A line whose `id` or `text`
   is not a string is skipped the same way.
2. **Normalize for detection.** Build a normalized copy of `text` by deleting every
   zero-width character: U+200B, U+200C, U+200D, U+FEFF. Every flag except `zero-width` is
   evaluated against that normalized text.
3. **Flags.** Check all that apply. These are the only flags:

   | flag | fires when |
   | --- | --- |
   | `base64-payload` | the normalized text matches the regex `(base64:\|\[base64\])\s*[A-Za-z0-9+/]{16,}`, case-insensitive. The marker must be followed by **at least 16** base64 characters. |
   | `delimiter-spoof` | the normalized text contains any of `<\|im_start\|>`, `<\|im_end\|>`, `[INST]`, `[/INST]`, `<<SYS>>`, `<</SYS>>` - verbatim, case-sensitive |
   | `exfiltration` | the normalized text matches the regex `!\[[^\]]*\]\(https?://[^)]*\)`, case-insensitive: markdown image syntax pointing at `http://` or `https://` |
   | `override` | the normalized text, lowercased, contains any of `ignore previous instructions`, `ignore all previous instructions`, `disregard all prior`, `you are now dan`, `system prompt override` |
   | `zero-width` | the **original** text contained at least one of the four zero-width characters |

4. **Verdict.** `flagged` when at least one flag fires, otherwise `clean`. An input that
   merely discusses prompt injection is clean: nothing outside the table above counts.

## Output

Write exactly these files to `$OUT`:

1. **`out/screened.csv`** - header `id,source,verdict,flags`. One row per surviving record,
   sorted by `id` ascending (byte-wise, `LC_ALL=C`). No id is duplicated in this corpus, so
   there is no tie-break to worry about. `verdict` is `clean` or `flagged`. `flags` is the
   firing flags in alphabetical order joined with `;`, or empty when nothing fired. No
   field contains a comma, so no quoting.
2. **`out/summary.json`** - an object with exactly these keys:
   - `total_inputs` (int) - surviving records
   - `clean_count` (int)
   - `flagged_count` (int)
   - `by_flag` (object) - flag name -> number of records carrying it, including **only**
     flags that fired at least once, with keys in alphabetical order

## Messes to expect

- `msg-004` hides `ignore previous instructions` behind a U+200B between `ig` and `nore`:
  it only matches after normalization, and it carries both `override` and `zero-width`
- `msg-008` has a `[BASE64]` marker with an 11-character payload: not enough, stays clean
- `msg-003` has the same marker with 27 characters: `base64-payload`
- `msg-013` is upper case; `msg-008` writes the marker as `[BASE64]` - matching is
  case-insensitive where the table says so
- `msg-006` carries two flags: `delimiter-spoof` and `override`
- `msg-014` is only zero-width obfuscation, so it is `flagged` with a single flag
- `msg-015` has `source: null`, so its `source` column is empty
- the corpus has a truncated JSON line, an array, a record with a numeric `id`, and a
  record with no `id`: four skipped lines, none of them counted
- some lines carry trailing whitespace, plus blank lines between records

## Timebox

Four minutes. If you are past that, the approach is wrong.
