"""Grader for 166-ruby-integer-division.

Expected values derived from fixtures/balances.csv by hand: floor division, not
truncation, on the negative accounts.
"""

import verifylib

EXPECTED = [
    ("alice", 15, 3, 5, 0),
    ("bob", -15, 2, -8, 1),
    ("carol", 9, 1, 9, 0),
    ("dana", -7, 2, -4, 1),
    ("erin", 5, 3, 1, 2),
]

EXPECTED_SUMMARY = {"accounts": 5, "total": 7, "negative_accounts": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "averages.csv",
        ["account", "sum", "count", "avg_cents", "carry"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
