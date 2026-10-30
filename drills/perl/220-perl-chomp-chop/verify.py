"""Grader for 220-perl-chomp-chop.

alpha, bravo, gamma: five characters each, fifteen in total, and the last
record is `gamma` — a chop-based solution loses its final `a`.
"""

import verifylib

EXPECTED = [
    (1, "alpha", 5),
    (2, "bravo", 5),
    (3, "gamma", 5),
]

EXPECTED_SUMMARY = {"notes": 3, "chars": 15, "last": "gamma"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "notes.csv",
        ["index", "text", "length"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
