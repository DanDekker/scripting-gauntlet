# 120-junit-report

> "The dashboard wants one row per test plus a summary. Our runner wrote counts into the
> report attributes and they are wrong — it never updated them. Count the testcases
> yourself and tell me which test was slowest."

## Input

`in/report.xml` — a JUnit-style XML report:

```xml
<testsuites name="all" tests="12" failures="2" errors="0" time="9.999">
  <testsuite name="suite.a" tests="3" failures="1" errors="0" time="0.900">
    <testcase classname="pkg.mod" name="test_one" time="0.10"/>
    <testcase classname="pkg.mod" name="test_two" time="0.20">
      <failure message="assert 1 == 2">stack trace line</failure>
    </testcase>
  </testsuite>
</testsuites>
```

The `tests`, `failures`, `errors` and `time` attributes on `<testsuites>` and
`<testsuite>` are **wrong**. They are noise. Only the `<testcase>` elements are truth.

## Rules

1. **Only `<testcase>` elements count.** One row per testcase, in document order.
   `classname` defaults to the empty string when the attribute is absent; `name` defaults
   to the empty string too. The suite of a testcase is the `name` of the `<testsuite>`
   that contains it — a `<testsuite>` with no `name` contributes the empty string.
2. **Status**, in this priority order:
   - `error` — the testcase has an `<error>` child (even if it also has a `<failure>`).
   - `fail` — the testcase has a `<failure>` child (even if it also has a `<skipped>`).
   - `skip` — the testcase has a `<skipped>` child and no `<failure>` and no `<error>`.
   - `pass` — none of those children.
3. **Duration** is the `time` attribute parsed as a float; a missing `time` (or a
   non-numeric one) is `0`. Durations are summed and printed with exactly 3 decimals.
4. **XML entities are decoded** in attribute values: `&quot;` -> `"`, `&amp;` -> `&`,
   `&lt;` -> `<`, `&gt;` -> `>`, `&apos;` -> `'`. This is visible in `name`/`classname`
   (e.g. `test_config &amp; env` is written `test_config & env`).
   The `<failure>` `message` is decoded too, but no output column carries it — the
   dashboard only wants counts.

## Output

Write exactly these files to `$OUT`:

1. **`out/tests.csv`** — header `suite,class,name,status,time`. One row per testcase, in
   **document order** (no sorting). `status` is exactly `pass`, `fail`, `error` or `skip`.
   `time` is always written with exactly 3 decimals (`0.000`, `1.250`, `0.500`).
2. **`out/summary.json`** — an object with exactly these keys:
   - `tests` — number of testcases (int)
   - `passed`, `failed`, `errored`, `skipped` — counts per status (int)
   - `time` — total duration, a number with 3 decimals
   - `slowest` — the `name` of the testcase with the greatest duration; **ties go to the
     first such testcase in document order**; the empty string when there are no
     testcases

## Messes to expect

- the `tests="12"` on `<testsuites>` is a lie: there are 10 testcases, 3 failures and
  2 errors, and the suite-level `time` values do not add up to the total
- a testcase with both `<failure>` and `<skipped>` counts as `fail` (skipped does not win)
- a testcase with both `<error>` and `<failure>` counts as `error`
- a `<failure message>` full of `&gt;`, `&quot;` and `&amp;` — a regex that stops at the
  first `>` will misparse it
- a testcase with no `time` attribute at all: it contributes `0.000`
- a testcase with no `classname`, and a `<testsuite>` with no `name`: both are empty cells
- a testcase name containing spaces, and one whose `&amp;` must come out as `&`
- two testcases share the slowest duration: `test_four` comes first in the document, so
  it is the `slowest`

## Fixture shape (a quirk you may lean on)

Every element opens and closes on one line, and a child element is never nested inside
another element's start tag line — so a line-oriented awk pass can read this file. Blank
lines, comment lines and trailing whitespace between elements are noise.

## Timebox

Four minutes. If you are past that, the approach is wrong.
