# 114-md-links

> "Docs rotted again — half the cross-references in this folder point at headings that
> don't exist any more. Walk the tree and tell me which links are fine, which files are
> missing, and which anchors no longer resolve."

## Input

`in/docs/` — a directory of markdown files, possibly nested. **Every** `.md` file under it,
recursively, is a source file; other file types are not scanned (but can be link targets).
Paths in the fixture are plain ASCII except one file name with a space (`my file.md`).

Links appear as inline markdown: `[text](target)`. The same line may carry several links;
they are considered left to right. Topics in the fixture: a link to a missing file, a link
to an existing file whose anchor is missing, a link to an existing file with a matching
anchor, a fragment-only link, external URLs, a markdown-looking link inside a fenced code
block, an anchor that differs only in case from the heading, a duplicate heading in one
file, a heading with trailing punctuation, a target with `%20` in it, a link to a
directory, and an empty target.

## Rules

1. **Fences.** A line whose trimmed text starts with ``` ``` ``` or `~~~` toggles the fence
   state and is never a link line. While a fence is open, every line is ignored (its links
   and its headings are not scanned).
2. **Which targets are rows.** A target that, after trimming surrounding whitespace, starts
   with `http://`, `https://` or `mailto:` is **external**: it is never checked and gets no
   row (but it is counted in `external`). Any other target gets a row. All non-external
   targets in this fixture are relative paths or fragments.
3. **Empty.** A target that is empty after trimming is reported with status `empty`.
4. **Anchors of a file.** For every ATX heading — one to six `#` followed by a space — the
   heading text is what follows the `#`s, trimmed. The anchor is that text **lowercased**,
   with every run of characters outside `a-z0-9` replaced by a single `-`, then leading and
   trailing `-` stripped. So `## Setup.` gives `setup`, `## Deep Dive` gives `deep-dive`,
   and `## Setup` in the same file gives the same anchor again (a duplicate is simply the
   same anchor; membership is what is checked). Matching is **case-sensitive**: `#Overview`
   does not match the anchor `overview`.
5. **Resolution.**
   - A **fragment-only** target (`#anchor`) is checked against the anchors of the file that
     contains the link.
   - A target with a path (`other.md`, `./sub/other.md`, `../other.md`,
     `other.md#section`) is resolved relative to the **directory of the file containing the
     link**, after decoding `%20` to a space and normalising `.` and `..`.
   - Status: `broken` when the resolved path does not exist; `missing-anchor` when the path
     exists but a fragment was given and is not one of that file's anchors; otherwise `ok`.
   - A path that exists but is a directory is `ok`. A path that exists and is not `.md` is
     `ok`. An existing path with no fragment is `ok`.

## Output

Write exactly these files to `$OUT`:

1. **`out/links.csv`** — header `file,line,target,status`. One row per non-external link.
   - `file` — path of the containing file relative to `in/docs`, using `/` separators.
   - `line` — 1-based line number inside that file.
   - `target` — the raw target text with surrounding whitespace stripped, **not** decoded
     (`my%20file.md` stays `my%20file.md`).
   - `status` — exactly `ok`, `broken`, `missing-anchor` or `empty`.
   - Order: files sorted by `file` ascending (byte order), then by line number ascending,
     then by order of appearance within the line.
   - No target in this fixture contains a comma, so plain unquoted CSV is expected.
2. **`out/summary.json`** — an object with exactly these keys:
   - `files` — `.md` files found under `in/docs` (int)
   - `links` — rows written to `links.csv` (int)
   - `ok`, `broken`, `missing_anchor`, `empty` — counts of each status (int); note
     `missing_anchor` uses an underscore
   - `external` — external targets skipped (int)

## Messes to expect

- the fenced block in `README.md` contains two markdown-looking links; neither is a row and
  the `# a code comment` line inside it is not a heading
- `#Overview` is `missing-anchor` even though `## Overview` exists — anchor matching is
  case-sensitive
- `sub/other.md#setup` is `ok` although the heading is `## Setup.` — trailing punctuation is
  removed by the anchor rule
- `my%20file.md` resolves to `my file.md` and is `ok`, but the reported target keeps `%20`
- `sub/` is a directory that exists, so it is `ok`; `nowhere/` does not exist, so `broken`
- `[]()` is an `empty` row, not a broken link
- `guide/advanced.md` reaches `../sub/other.md` from one level down; normalising `..` is the
  whole trick
- `./deep.md` from `sub/nested/` resolves to `sub/nested/deep.md`, which does not exist

## Timebox

Four minutes. If you are past that, the approach is wrong.
