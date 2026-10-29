# 126-window-split

> "The prompt budget is 200 characters and the doc is much longer. Cut it into windows I can
> feed one at a time, keep a little overlap so the model does not lose the thread, and never
> hand me a window that is over budget."

## Input

- `in/doc.txt` — one document, paragraphs separated by blank lines.
- `in/config.json` — `{"max_chars": 200, "overlap": 50}`.

The document is messy on purpose: trailing whitespace inside paragraphs, a trailing-space-only
line as a paragraph of its own, several blank lines in a row, a literal Windows path with
backslashes, a quoted phrase with real `"` characters, punctuation and commas, a paragraph far
longer than the budget, and a final paragraph with no newline after it.

## Rules

1. **Paragraphs.** A line that is empty after trimming is a separator. A paragraph is a run of
   consecutive non-empty lines; its text is the lines with their **trailing** whitespace
   stripped, joined with a single `\n`, and then the whole thing trimmed at both ends. A
   paragraph that is empty after that is dropped: it is not a window and does not count.
2. **Window text.** A window is built from *parts*: an optional overlap prefix, then one or
   more paragraphs, joined with `\n\n` (two characters between consecutive parts). Its length
   is `len(text)` — characters, and the newlines count.
3. **Packing.** Start a window with the next unfilled paragraph. Keep appending the following
   paragraph while the joined text stays within `max_chars`. When the next paragraph would
   push it over, close the window and start a new one.
4. **Overlap.** Every window after the first starts with a prefix: the **last `overlap`
   characters** of the previous window's text. If that prefix alone is longer than
   `max_chars` it is cut to its own last `max_chars` characters. If the prefix does not leave
   room for the next paragraph — `len(prefix) + 2 + len(paragraph) > max_chars` — the prefix is
   **dropped** and the window starts clean with the paragraph. `overlap` 0 means never a
   prefix.
5. **Long paragraph.** A single paragraph longer than `max_chars` is **split** into consecutive
   pieces of `max_chars` characters (the last piece is whatever is left). Each piece is one
   window on its own, with no prefix and no other paragraph. The window after the last piece
   takes its prefix from that piece like any other window.

## Output

Write exactly these files to `$OUT`:

1. **`out/windows.csv`** — header `index,chars,text`, one row per window in order. `index`
   starts at 1. `chars` is the length of the window's full text.
   `text` is the window's full text with every newline shown as the two characters `\n`
   (backslash, n) so the row stays on one line, and every literal backslash doubled to `\\` —
   backslashes are escaped **first**, then newlines. The field is always wrapped in double
   quotes, and every `"` inside the text is written as `""` (normal CSV quoting), because the
   text contains commas.
2. **`out/summary.json`** — an object with exactly these keys:
   - `paragraphs` — surviving paragraphs (int)
   - `windows` — windows written (int)
   - `chars` — total characters across all windows, overlap prefixes included (int)
   - `max_window` — the greatest `chars` of any window, `0` when there are none (int)
   - `overlap` — the configured overlap (int)

## Messes to expect

- the trailing-space-only line is a separator, not a paragraph: `paragraphs` is 5
- the trailing spaces on the end of the importer paragraph and the long paragraph are stripped
  before anything is counted
- the Windows path keeps its backslashes, each doubled in the CSV (`C:\\tmp\\ledger\\import`)
- the quoted phrase comes out as `""how long""` in the raw CSV and as `"how long"` once parsed
- the second window has **no** prefix: `50 + 2 + 156 > 200`, so rule 4 drops it
- the third window starts with the 50-character tail of the second, which lands mid-word at
  `e file every five minutes, ...`
- the long paragraph becomes three windows (`200`, `200`, `41` characters) — it is cut, never
  dropped
- the last window is the 41-character tail of the final piece plus the closing paragraph

## Timebox

Four minutes. Do not try to balance windows; a greedy pack with a tail is the whole job.
