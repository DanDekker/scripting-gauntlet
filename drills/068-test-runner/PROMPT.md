# 068-test-runner

> "Run this small smoke suite the same way on Linux, macOS, and Windows. I want one
> result per case, and a failing case must make the suite command fail."

## Task

Read test names from `in/tests.txt`. Run each in a separate child process:

```text
python test_case.py <name>
```

Use `python3`, `python`, or `py -3` as available. The tests read fixtures from `$IN`.

## Rules

1. Skip blank lines and `#` comments. Names contain lowercase letters and hyphens.
2. Run tests in listed order. Capture stdout, stderr, and the exit code for every case.
   Each fixture test emits at most one line, with no commas.
3. Continue through the full list even when a test exits non-zero.
4. Write the report before exiting. The suite command exits `1` if any case failed,
   `0` if all passed. On an invalid test-list row, name it on stderr and exit non-zero.

## Output

- `out/results.csv`: header `test,exit_code,stdout,stderr`, one row per case in list order.
- `out/summary.json`: exactly `tests`, `passed`, and `failed`, all integers.

## Messes to expect

- blank and comment lines in the test list
- a test list that must be run in order
- each test is a child process, so one failure must not prevent later cases from running

## Timebox

4 minutes. Put each invocation in an `if` so `set -e` preserves its exit code.
