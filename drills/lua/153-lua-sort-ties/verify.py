"""Grader for 153-lua-sort-ties.

Expected values derived from fixtures/scores.txt by hand: 6 accepted records, 1 invalid
line, 5 records sharing a score, and cross-checked against the lua and python references.
"""

import verifylib

EXPECTED = [
    ("alpha", 30, 1),
    ("beta", 30, 2),
    ("epsilon", 30, 5),
    ("delta", 10, 4),
    ("eta", 10, 6),
    ("gamma", 9, 3),
]

EXPECTED_SUMMARY = {"records": 6, "invalid": 1, "tied": 5}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "sorted.csv", ["name", "score", "index"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
