"""Grader for 176-ps1-group-folding.

Expected values derived from fixtures/items.csv by hand: case-sensitive groups, empty
amounts counted as missing, ordinal order.
"""

import verifylib

EXPECTED = [
    ("Web", 1, 5, 0),
    ("cache", 1, 0, 1),
    ("db", 2, 10, 0),
    ("web", 2, 10, 1),
]

EXPECTED_SUMMARY = {"groups": 4, "items": 6, "missing": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "groups.csv", ["group", "count", "total", "missing"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
