"""Grader for 172-lua-coroutine-pipeline.

Expected values derived by hand: five good records before the fatal sixth line.
"""

import verifylib

EXPECTED = [
    ("error", 7, 1),
    ("info", 33, 3),
    ("warn", 5, 1),
]

EXPECTED_SUMMARY = {"lines": 6, "processed": 5, "aborted": 6, "levels": 3}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "totals.csv", ["level", "total", "count"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
