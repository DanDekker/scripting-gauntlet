"""Grader for 164-perl-hash-order.

Expected values derived from fixtures/events.log by hand: 5 users, 9 events, 1 invalid
line, and cross-checked against the perl and python references.
"""

import verifylib

EXPECTED = [
    ("alice", 3),
    ("bob", 3),
    ("10", 1),
    ("9", 1),
    ("carol", 1),
]

EXPECTED_SUMMARY = {"users": 5, "events": 9, "invalid": 1, "top": "alice"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "counts.csv", ["user", "events"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
