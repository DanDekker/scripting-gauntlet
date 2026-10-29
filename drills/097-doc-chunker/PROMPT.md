# 097-doc-chunker

> "I am building a retrieval index over a pile of markdown notes. Chunk them, give every
> chunk an id I can cite, and do not index the same paragraph twice just because someone
> kept a copy of the file."

## Input

`in/docs/` — a directory of `.md` files. Only files whose name ends in `.md` and that sit
**directly** inside `in/docs/` are documents; there are no subdirectories. Documents are
processed in ascending byte order of their file name (`faq.md` before `guide.md` before
`guide_v2.md` before `release-notes.md`).

The input is messy in realistic ways: one file is a byte-identical copy of another under a
different name, one paragraph is only whitespace, one file has no headings at all, one
paragraph is a long multi-line wall of text, and paragraphs carry trailing spaces.

## Rules

1. **Sections.** A *section* starts at every line whose first two characters are `# ` (hash,
   space). The section title is the rest of that line, trimmed. Text before the first such
   line belongs to a section titled `(preamble)`. A line starting with `## ` (two hashes) is
   **not** a heading: it is ordinary paragraph text, and it stays inside the current section.
2. **Paragraphs.** Inside a section the body is split into paragraphs at blank lines. A line
   is *blank* only when it is empty, or is a single carriage return (a CRLF file). A line
   holding only spaces or tabs is **not** blank — it is content, which is how a paragraph
   can end up empty after trimming.
3. **Trim.** For a paragraph, strip trailing spaces, tabs and carriage returns from each of
   its lines, join the lines back with `\n` (internal newlines are kept), then strip leading
   and trailing whitespace from the whole string. That trimmed string is the paragraph's
   text.
4. **Count.** `tokens` is the number of whitespace-separated words in the text. `chars` is the
   number of characters in the text (the fixture is ASCII, so characters and bytes agree).
5. **Drop empties.** A paragraph whose text is empty is dropped and counted in
   `empty_dropped`. It still occupies an index (see rule 8).
6. **Dedupe.** After empty paragraphs are dropped, paragraphs are considered in output order
   (document ascending, then index ascending). The first occurrence of a given text is kept;
   every later occurrence of the *byte-identical* text (case-sensitive, and regardless of
   which document or section it came from) is dropped and counted in `duplicates_dropped`.
7. **Chunk.** A surviving paragraph is one chunk. `doc` is the file name relative to
   `in/docs/`. `section` is the title of the section it appeared in.
8. **Ids.** The chunk id is `<doc>#<section>#<index>`, where `<index>` is the 1-based position
   of the paragraph **within its document**, counting every paragraph of that document in
   reading order — including paragraphs that were empty or deduplicated away. Ids therefore
   stay stable when a neighbour is dropped.

## Output

Write exactly these files to `$OUT`:

1. **`out/chunks.csv`** — header `id,doc,section,tokens,chars`. One row per surviving chunk,
   sorted by `doc` ascending (byte order) and then by the chunk's numeric `index` ascending
   (numeric, not lexicographic: index 10 comes after index 9). No row is written for a
   dropped chunk.
2. **`out/summary.json`** — an object with exactly these keys:
   - `documents` — number of `.md` files in `in/docs/` (int)
   - `total_chunks` — surviving chunks (int)
   - `duplicates_dropped` — paragraph occurrences dropped by rule 6 (int)
   - `empty_dropped` — paragraph occurrences dropped by rule 5 (int)
   - `tokens` — sum of `tokens` over surviving chunks (int)

## Messes to expect

- `guide_v2.md` is byte-identical to `guide.md`; its paragraphs dedupe against `guide.md`,
  which sorts first, so it contributes no rows at all
- the whitespace-only paragraphs (a single space on its own line in `faq.md`, a single
  tab on its own line in `release-notes.md`) are *not* paragraph separators: each becomes an
  empty paragraph, is dropped, and burns an index
- `## Usage` is body text and is its own paragraph, so it has `tokens` 2
- trailing spaces after `pip.` and after `log.` must not reach `chars`
- the long paragraph in `guide.md` is a single chunk: newlines inside a paragraph are not a
  split point

## Timebox

Five minutes. If you are past that, the approach is wrong.
