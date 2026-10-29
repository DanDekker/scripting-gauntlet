# 095-eval-rubric

> "I have a pile of eval cases and the model's answers. Score them — but each case type
> needs its own check, and I don't want a case counted as passing just because my rubric
> did not know how to judge it."

## Input

`in/cases.jsonl` — one JSON object per line:

```json
{"id":"c1","kind":"exact","expected":"42","actual":" 42 "}
```

- `id` (string) — the case identifier
- `kind` — `exact`, `contains`, or `number`
- `expected` — the reference answer (string)
- `actual` — the model output (string)

The file is messy: blank lines, a line that is not valid JSON, a line that is valid JSON
but not an object, an unknown `kind`, a `number` case whose `expected` is not a number, and
strings padded with spaces.

## Rules

1. **Skip junk.** Blank lines, lines that are not valid JSON, and lines that are JSON but
   not an object are skipped and are **not** counted anywhere. Every surviving object is a
   case, in input order.
2. **Trim first.** Every matcher compares the strings after stripping leading and
   trailing whitespace. A missing `expected`/`actual` is treated as the empty string.
3. **Matchers**, chosen by `kind`:
   - `exact` — the trimmed strings are equal, **case-sensitive**.
   - `contains` — the trimmed `actual` contains the trimmed `expected` as a substring,
     case-insensitively.
   - `number` — both trimmed sides parse as floats and `abs(expected - actual) <= 0.01`.
     If either side does not parse as a number, the case **fails**.
4. **Unknown kind fails.** A `kind` that is not one of the three above fails the case. The
   case still appears in the output, with its `kind` verbatim, so the bad rubric is
   visible.

## Output

Write exactly these files to `$OUT`:

1. **`out/scores.csv`** — header `id,kind,passed`. One row per surviving case, in input
   order. `passed` is exactly `true` or `false` (lowercase). `kind` is the case's `kind`
   verbatim, including an unknown one.
2. **`out/summary.json`** — an object with exactly these keys:
   - `total` — surviving cases (int)
   - `passed` — cases that passed (int)
   - `failed` — cases that failed (int)
   - `pass_rate` — `passed / total` rounded to 4 decimals (float); `0` when `total` is 0

## Messes to expect

- the invalid-JSON line and the non-object line are not cases: `total` counts only real
  objects
- ` 42 ` vs `42` passes `exact`; `paris` vs `Paris` does **not** (`exact` is case-sensitive)
- `TIMEOUT` matches `timeout` under `contains` (that one is case-insensitive)
- `3.14` vs `3.141` passes `number`; `1.0` vs `1.5` does not
- `expected` = `n/a` on a `number` case fails instead of raising
- `kind` = `regex` fails and is reported — an unjudgeable case is a failure, not a skip

## Timebox

A few minutes. If you are past that, the approach is wrong.
