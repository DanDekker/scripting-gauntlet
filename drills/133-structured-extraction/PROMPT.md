# 133-structured-extraction

> "I logged a few hundred assistant replies and I want the payloads out of them. Each reply
> is chatty — a preamble, maybe a fenced block, maybe an apology, sometimes the JSON is just
> sitting in the middle of a sentence. Give me the ones that actually contain a JSON object
> or array, and tell me plainly which replies were unusable instead of guessing."

## Input

`in/responses.txt` — a transcript of assistant replies. Each reply starts with a header line

```
=== RESPONSE <id> ===
```

where `<id>` is a token with no spaces (e.g. `r01`). The header may carry trailing spaces.
Everything up to the next header line is that reply's block. Anything before the first
header is ignored.

A block may contain, in any combination:

- conversational preamble (`Sure! Here is the JSON you requested:`) and postscript
  (`Hope this helps!`)
- fenced code blocks: ` ```json ... ``` `, ` ``` ... ``` ` (no language), or some other
  language such as ` ```python ... ``` `
- bare JSON in running prose, with no fence at all
- several fenced blocks, only one of which holds the payload
- invalid JSON: truncated brackets, trailing commas, bare keys
- a JSON *primitive* (`42`, `"text"`, `true`) instead of an object or array
- empty content

## Rules

1. **One record per header, in file order.** A reply is never dropped from the report — an
   unusable reply is reported as `failed`.
2. **Candidate order.** For each block, collect candidate payload texts and take the first
   one that is valid, in this order:
   1. the contents of fenced blocks whose language tag is `json` (case-insensitive), in
      document order;
   2. the contents of fenced blocks with **no** language tag, in document order;
   3. every balanced `{ ... }` or `[ ... ]` span in the **raw block text** (fences and all),
      scanning left to right from each `{` or `[`, taking the matching close bracket while
      respecting JSON string quoting (a `{` inside `"..."` neither opens nor closes
      anything). Spans that do not balance are skipped and the scan continues with the next
      character. A span that balances but does not parse is skipped the same way.

   A fenced block with another language tag (`python`, `bash`, …) is never a candidate by
   itself — but its text is still part of the raw block scanned in step 3.
3. **Valid means object or array.** A candidate is valid only if it parses as a JSON object
   or a JSON array. A reply whose only parseable candidate is a number, string, boolean or
   `null` is `failed`: the payload you were asked for is a document, not a scalar.
4. **Deterministic output shape.** `type` is `object` or `array`. `keys_or_length` is the
   number of keys for an object, the element count for an array.

## Output

Write exactly these files to `$OUT`:

1. **`out/extracted.jsonl`** — one line per **successful** reply, in input order. Each line is
   compact single-line JSON (no spaces after `:` or `,`), keys in exactly this order:

   ```json
   {"id":"r01","type":"object","keys_or_length":3,"data":{"tool":"search"}}
   ```

   `data` is the extracted value itself — embedded as JSON, **not** re-encoded as a string.
   The file is empty (0 bytes) when nothing was extracted.
2. **`out/status.csv`** — header `id,status,type`. One row for **every** reply, in input
   order. `status` is `extracted` or `failed`; `type` is `object`, `array`, or `none`.
3. **`out/summary.json`** — object with exactly these keys:
   - `total_responses` (int)
   - `extracted_count` (int)
   - `failed_count` (int)
   - `objects_count` (int)
   - `arrays_count` (int)

## Messes to expect

- `r03` has a `python` fence before the `json` fence: the language tag is what makes the
  order safe.
- `r08`'s first `json` fence has trailing commas, so the *second* `json` fence wins.
- `r09`'s fence holds a bare string — parseable, rejected, so the object in the prose wins.
- `r10`'s preamble contains a template placeholder `{config}`: a scanner that only looks
  for `{` and the first `}` grabs `{config}`, fails, and must keep looking.
- `r11` has an unlabelled fence with an array **before** a `json` fence with an object: the
  labelled fence wins, position notwithstanding.
- `r06` parses cleanly and is still `failed`; `r05` is truncated; `r07` is empty; `r12` has
  no JSON at all.

## Timebox

A few minutes. If you are past that, the approach is wrong.
