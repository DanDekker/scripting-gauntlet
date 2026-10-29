# 103-ci-triage

> "The build went red and the log is 4000 lines. Tell me which tests actually failed,
> which errored, which were skipped, and which passed — one line per test."

## Input

`in/ci.log` — a captured CI log. It contains:

- a `=== test session starts ===` header and assorted setup text
- result lines of the form `<STATUS> <test-id>` where `STATUS` is `PASSED`, `FAILED`,
  `ERROR` or `SKIP` and `test-id` looks like `tests/test_api.py::test_ping`
- tracebacks and captured-log blocks that may mention `FAILED` in the middle of a line
- a `=== short test summary info ===` marker, then `FAILED <test-id> - <reason>` lines
- ANSI colour escapes (`ESC [ 31 m`, `ESC [ 0 m`) around some result lines
- blank lines

## Rules

1. **Strip ANSI first.** Remove every `ESC [ … m` sequence from a line before looking at
   it, then trim leading and trailing whitespace.
2. **A result line** is a line whose trimmed content starts with `PASSED `, `FAILED `,
   `ERROR ` or `SKIP ` followed by a test id. The test id is the token after the status,
   up to the first whitespace (anything after it — `(reason: no fixture)`, `- AssertionError`
   — is ignored). A line that merely *contains* the word `FAILED` is not a result line:
   `RuntimeError: worker FAILED to start after 3 retries` is noise.
3. **The marker splits the file.** Before `=== short test summary info ===` any result line
   counts. At and after the marker, only lines of the form `FAILED <test-id> - <reason>`
   count; a `PASSED`/`SKIP`/`ERROR` line there is ignored. The marker appears exactly once
   and is not itself a result.
4. **Last result wins**, in log order — a test reported `FAILED` then `PASSED` (a rerun)
   ends up passing, and a test that only appears in the short summary exists.
5. **`ERROR` is sticky.** Once a test id has been seen with `ERROR`, its final verdict is
   `error` no matter what appears later: a test that errored did not really pass.
6. Missing from the log entirely is not a row: only test ids that had at least one result
   appear in the output.

## Output

Write exactly these files to `$OUT`:

1. **`out/results.csv`** — header `test,verdict`. One row per distinct test id that had
   any result, sorted by `test` ascending. `verdict` is exactly `pass`, `fail`, `error` or
   `skip` (`PASSED`→`pass`, `FAILED`→`fail`, `ERROR`→`error`, `SKIP`→`skip`).
2. **`out/summary.json`** — an object with exactly these keys:
   - `tests` — rows in `results.csv` (int)
   - `passed`, `failed`, `errored`, `skipped` — how many tests ended with each verdict (int)

## Messes to expect

- `tests/test_api.py::test_timeout` is `FAILED` then `PASSED`: verdict `pass`
- `tests/test_db.py::test_setup` is `ERROR` then `PASSED`: verdict `error` (sticky)
- `tests/test_db.py::test_seed` is `PASSED` then `ERROR` later: verdict `error`
- `tests/test_cache.py::test_evict` is `FAILED`, then `PASSED`, then `FAILED` in the short
  summary: verdict `fail`
- `tests/test_queue.py::test_drain` appears only in the short summary: a row, `fail`
- the traceback lines that mention `FAILED` mid-line produce no rows
- three result lines are wrapped in ANSI colour: unstripped they would not be recognised

## Timebox

A few minutes. If you are past that, the approach is wrong.
