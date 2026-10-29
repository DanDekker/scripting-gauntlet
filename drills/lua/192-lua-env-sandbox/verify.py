"""Grader for 192-lua-env-sandbox.

Expected results derived from expressions.txt and sandbox constraints:
1: abs(-42) -> 42 (ok)
2: upper("alice") -> ALICE (ok)
3: os.execute -> runtime_error (attempt to index nil global 'os')
4: 10 * 2 + 5 -> 25 (ok)
5: syntax error -> compile_error
6: io.open -> runtime_error (attempt to index nil global 'io')
"""

import verifylib

EXPECTED = [
    (1, "ok", "42"),
    (2, "ok", "ALICE"),
    (3, "runtime_error", ""),
    (4, "ok", "25"),
    (5, "compile_error", ""),
    (6, "runtime_error", ""),
]

EXPECTED_SUMMARY = {
    "expressions": 6,
    "ok": 3,
    "runtime_error": 2,
    "compile_error": 1,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "results.csv",
        ["id", "status", "result"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
