"""Grader for 173-lua-load-sandbox.

Expected values derived from the Lua 5.5 probe: the sandbox refuses os/nope by name,
`2 +` is a compile error, `1 // 0` is a runtime error, and `1 / 0` is ok (inf).
"""

import verifylib

EXPECTED = [
    ("1 + 2", "ok", "3"),
    ("abs(-3)", "ok", "3"),
    ("floor(3.7)", "ok", "3"),
    ("max(1, 5, 2)", "ok", "5"),
    ("os.time()", "runtime", "unknown name: os"),
    ("nope + 1", "runtime", "unknown name: nope"),
    ("2 +", "syntax", "unexpected symbol near <eof>"),
    ("1 // 0", "runtime", "attempt to divide by zero"),
    ("'x' + 1", "runtime", "attempt to add a 'string' with a 'number'"),
    ("1 / 0", "ok", "inf"),
    ("'a' .. 'b'", "not_number", "ab"),
]

EXPECTED_SUMMARY = {"lines": 11, "ok": 5, "syntax": 1, "runtime": 4, "not_number": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "results.csv", ["expr", "status", "detail"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
