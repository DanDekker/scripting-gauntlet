"""Grader for 175-perl-version-sort.

Expected values derived by hand: 2.0.0 newest, the three 1.10.2 releases in name order,
then 1.9.9 and 1.2.10.
"""

import verifylib

EXPECTED = [
    (1, "gamma", "2.0.0"),
    (2, "alpha", "1.10.2"),
    (3, "delta", "1.10.2"),
    (4, "eta", "1.10.2"),
    (5, "beta", "1.9.9"),
    (6, "epsilon", "1.2.10"),
]

EXPECTED_SUMMARY = {"lines": 7, "ordered": 6, "invalid": 1, "newest": "gamma"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "ordered.csv", ["rank", "name", "version"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
