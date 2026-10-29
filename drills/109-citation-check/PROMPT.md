# 109-citation-check

> "The model wrote an answer with numbered claims and a source list. Before this goes out,
> tell me which claims no source actually backs — and don't let a claim through just because
> one of its words appears somewhere in a source."

## Input

- `in/answer.md` — an answer whose claims are one per line, in the form
  `Claim 1: the parser drops trailing whitespace` (the number may be missing:
  `Claim: something`). It also contains lines that are **not** claims: a `#` heading, blank
  lines, a paragraph of prose, and a `Sources:` line.
- `in/sources.txt` — one source snippet per line; each line is text a source can support.

Messes in the fixtures: a claim with no number, two claims sharing number `4`, a claim
whose text is empty after the colon, a `Claim` line with no colon at all, a claim line
indented two spaces, a claim whose text has a doubled internal space while its source has
single spaces, a source line with several internal spaces and trailing whitespace, an empty
source line, a whitespace-only source line, a claim that matches a source only
case-insensitively, a source that covers only the **beginning** of a claim, and a source
holding the claim's words in a different order.

## Rules

1. **What is a claim line.** A line whose *trimmed* text starts with `Claim` (that word is
   case-sensitive) followed by either `:` or one or more spaces then digits then `:`. So
   `Claim: x`, `Claim 4: x` and `Claim 6:` are claims; `Claim something`,
   `Claim 7 something` and `Claims are prose` are not claims and count nowhere.
2. **The claim text** is everything after that colon, trimmed. A claim whose text is empty
   is still a claim line, but it can never be supported.
3. **Claim numbers.** A numbered claim uses its number (the integer value of the digits).
   An unnumbered claim is numbered by its 1-based position among claim lines. Two claims
   with the same number are both kept.
4. **Supported** means: some source line contains the claim text in full, after both sides
   are lowercased and every internal whitespace run is collapsed to a single space. A
   source that only covers the beginning of a claim does **not** support it — the claim
   text has to fit inside the source, so a claim longer than its source is unsupported. The
   same words in a different order are not a match. An empty claim text is unsupported.
5. **A source** is a line of `sources.txt` whose trimmed text is non-empty; empty and
   whitespace-only lines are not sources and are not counted.

## Output

Write exactly these files to `$OUT`:

1. **`out/claims.csv`** — header `number,supported,text`. One row per claim line, including
   unsupported claims and claims whose text is empty. Sorted by `number` ascending; rows
   with the same number keep their original line order. `supported` is exactly `true` or
   `false`. `text` is the trimmed claim text — an empty string when the claim had none —
   with its internal spacing left as written (whitespace is collapsed only for the
   comparison, never in the output).
2. **`out/summary.json`** — an object with exactly these keys:
   - `claims` — claim lines (int)
   - `supported` — claims that are supported (int)
   - `unsupported` — claims that are not (int)
   - `sources` — non-empty source lines (int)
   - `unsupported_numbers` — the numbers of the unsupported claims, ascending, without
     duplicates (list of ints)

## Messes to expect

- `Claim: the loader ignores blank lines` has no number, so it becomes the third claim and
  is numbered `3`.
- `Claim 4:` appears twice: both rows survive, in file order, one supported and one not.
- `Claim 6:` has empty text: it counts as a claim, is unsupported, and its row's `text` is
  empty.
- `retries are  capped at three attempts` (two spaces) is supported by the source that has
  one space there — the comparison collapses whitespace, the output column keeps it.
- `The Parser Drops Trailing Whitespace` is supported only case-insensitively.
- `the retry loop never backs off` appears in no source in that order → unsupported.
- `the cache warms on first read of the config` is longer than its source → unsupported.

## Timebox

Five minutes. If you are past that, the approach is wrong.
