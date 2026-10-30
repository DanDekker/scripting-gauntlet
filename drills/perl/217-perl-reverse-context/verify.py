"""Grader for 217-perl-reverse-context.

Reversed order: charlie three, bravo two, alpha one.
"""

import verifylib

EXPECTED = [
    (1, "charlie three"),
    (2, "bravo two"),
    (3, "alpha one"),
]

EXPECTED_SUMMARY = {"records": 3, "first": "charlie three", "last": "alpha one"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "records.csv",
        ["index", "record"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
