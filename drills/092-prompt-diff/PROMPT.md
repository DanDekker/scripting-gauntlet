# 092-prompt-diff

> "I rewrote the agent's system prompt. Before I ship v2, tell me exactly what changed —
> and whether I quietly dropped a rule it must never break."

## Input

- `in/prompt_v1.txt` — the prompt as it is in production.
- `in/prompt_v2.txt` — the candidate rewrite.

One instruction per line, plain text. Both files are messy on purpose: trailing spaces,
blank and whitespace-only lines, a duplicated instruction, CRLF line endings in one
file, and at least one instruction that differs between versions only in its internal
spacing.

## Rules

1. **Normalize every line.** Drop carriage returns, collapse every internal run of
   whitespace (spaces, tabs) to a single space, then strip leading and trailing
   whitespace. Discard the line if it is empty after that.
2. **Collapse duplicates.** After normalization each distinct line counts once, at the
   position of its first occurrence. A line repeated inside one version is one line.
3. **Classify.** A normalized line is:
   - `removed` — present in v1, absent from v2
   - `added` — present in v2, absent from v1
   - `unchanged` — present in both
4. **Guardrail.** A removed line is a guardrail when it contains — case-insensitively —
   any of these substrings: `must`, `never`, `do not`, `don't`, `should not`.

A whitespace-only edit is **not** a change: an instruction that appears in both versions
modulo spacing is `unchanged`.

## Output

Write exactly these files to `$OUT`:

1. **`out/changes.csv`** — header `change,line`. One row per changed line: all `removed`
   rows first, in the order the lines appear in v1; then all `added` rows, in the order
   they appear in v2. `change` is exactly `removed` or `added`. `line` is the normalized
   instruction. Use standard CSV quoting (a line containing a comma is quoted).
2. **`out/summary.json`** — an object with exactly these keys:
   - `removed` — number of removed lines (int)
   - `added` — number of added lines (int)
   - `unchanged` — number of lines present in both versions (int)
   - `guardrails_removed` — number of removed lines that are guardrails (int)

## Messes to expect

- CRLF endings: `Never ...` and `Never ...\r` are the same line.
- trailing whitespace and whitespace-only lines must not create a change
- the duplicated instruction counts once and must not inflate `unchanged`
- internal double spaces: `Keep  answers  short.` and `Keep answers short.` are the same
  line
- a line that differs between versions only in **case** is a real change — the line
  comparison is case-sensitive; only the guardrail classification ignores case

## Timebox

A few minutes. If you are past that, the approach is wrong.
