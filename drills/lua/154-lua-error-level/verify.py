"""Grader for 154-lua-error-level.

Expected values derived from fixtures/records.txt by hand: 12 lines, 6 accepted, 5
failures, and cross-checked against the lua and python references.
"""

import verifylib

EXPECTED_ERRORS = [
    (4, "not an integer: three"),
    (8, "duplicate key: alpha"),
    (9, "missing '='"),
    (10, "not an integer: -3"),
    (11, "bad key: two words"),
]

EXPECTED_ACCEPTED = [
    ("alpha", "1"),
    ("beta", "2"),
    ("delta", "4"),
    ("eps", "5"),
    ("zeta", "6"),
    ("eta", "8"),
]

EXPECTED_SUMMARY = {"lines": 12, "accepted": 6, "errors": 5}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "errors.csv", ["line", "reason"], EXPECTED_ERRORS, key_count=1
    )
    failures += verifylib.keyed_table(
        io.out / "accepted.csv", ["key", "value"], EXPECTED_ACCEPTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
