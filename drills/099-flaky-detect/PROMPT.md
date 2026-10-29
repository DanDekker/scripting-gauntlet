# 099-flaky-detect

> "CI is red half the time and nobody believes the results any more. Out of this run history,
> tell me which tests are actually flaky — not which ones are broken, not which ones are
> solid — and how often each one flips."

## Input

`in/history.jsonl` — one JSON object per line, one line per test run:

```json
{"test": "test_login", "passed": true, "duration_ms": 120}
```

The file is messy in realistic ways: blank lines, a line that is not JSON at all, a line that
is JSON but an array instead of an object, an object whose `test` is a number, an object whose
`test` is only spaces, an object with a trailing comma (so the line does not parse), a test
name with spaces around it, a `passed` value written as the string `"true"` (and `" TRUE "`),
and a `passed` value of `null`.

## Rules

1. **Skip junk.** A blank line, a line that is not valid JSON, and a line that parses to
   something other than a JSON object are skipped. A skipped line is not a run: it counts
   nowhere.
2. **A record needs a name.** An object is a record only when `test` is a string that is
   non-empty after trimming; `test` is then that trimmed name. An object with a missing,
   non-string or blank `test` is skipped like junk.
3. **Decide `passed`.** The run passed when `passed` is the boolean `true`, or the string
   `"true"` compared case-insensitively after trimming. Everything else is a failure: boolean
   `false`, the string `"false"`, `null`, a missing `passed` key, or any other value.
4. **Classify each test** from its own runs:
   - *flaky* — at least one pass **and** at least one failure
   - *stable-pass* — every run passed (a test seen exactly once with a pass is stable-pass)
   - *stable-fail* — no run passed (a test seen exactly once with a failure is stable-fail)

## Output

Write exactly these files to `$OUT`:

1. **`out/flaky.csv`** — header `test,total,passed,failed,fail_rate`. One row per **flaky**
   test only — a test that only ever failed is not flaky and must not appear here. Sorted by
   `test` ascending (byte order). `total`, `passed` and `failed` are that test's run counts.
   `fail_rate` is `failed / total` rounded to 4 decimals and printed with exactly four
   decimal places: `0.6000`, `0.3333`, `0.5000` — never `0.6`.
2. **`out/summary.json`** — an object with exactly these keys:
   - `tests` — distinct test names across surviving records (int)
   - `flaky` — tests classified flaky (int)
   - `stable_pass` — tests classified stable-pass (int)
   - `stable_fail` — tests classified stable-fail (int)
   - `runs` — surviving records, i.e. every run that was not skipped (int)

## Messes to expect

- `"passed": " TRUE "` is a pass; `"passed": null` and a missing `passed` key are failures
- `"test": " test_checkout "` is the same test as `test_checkout` after trimming
- the array line, the numeric-`test` line, the blank-`test` line and the trailing-comma line
  never become runs, so `runs` is smaller than the number of lines in the file
- `test_solo_fail` (one run, failed) is stable-fail, not flaky; `test_once` (one run, passed)
  is stable-pass
- a test with three runs, two passes and one failure has `fail_rate` `0.3333`

## Timebox

Four minutes. If you are past that, the approach is wrong.
