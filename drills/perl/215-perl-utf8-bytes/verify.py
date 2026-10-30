"""Grader for 215-perl-utf8-bytes.

café, Jörg are 4 characters each; zoë is 3; marguerite is 10.
Total 3+4+4+3+10 = 24.
"""

import verifylib

EXPECTED = [
    (1, "ADA", 3),
    (2, "CAFÉ", 4),
    (3, "JÖRG", 4),
    (4, "ZOË", 3),
    (5, "MARGUERITE", 10),
]

EXPECTED_SUMMARY = {"names": 5, "chars": 24, "longest": 10}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "names.csv",
        ["index", "name", "chars"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
