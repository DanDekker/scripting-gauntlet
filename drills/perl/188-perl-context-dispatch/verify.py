"""Grader for 188-perl-context-dispatch.

Expected values derived from fixtures/records.txt:
Scores >= 70: ids 1, 3, 5 (count = 3)
Scores >= 90: ids 3, 5 (count = 2)
Query 3 (list_first) must capture ID 1, not count 3!
"""

import verifylib

EXPECTED = [
    (1, "scalar", "3"),
    (2, "list", "1;3;5"),
    (3, "list_first", "1"),
    (4, "scalar", "2"),
]

EXPECTED_SUMMARY = {"queries": 4, "list_queries": 2, "scalar_queries": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "dispatches.csv",
        ["caller", "context", "result"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
