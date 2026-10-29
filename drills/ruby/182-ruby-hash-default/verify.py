"""Grader for 182-ruby-hash-default.

Expected values derived by hand from fixtures/events.txt.
"""

import verifylib

EXPECTED = [
    ("alice", 3, "login;login;view"),
    ("bob", 2, "login;view"),
    ("carol", 1, "login"),
]

EXPECTED_SUMMARY = {"users": 3, "events": 6}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "tally.csv", ["user", "count", "tags"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
