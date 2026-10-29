"""Grader for 181-perl-substr-index.

Expected values derived by hand from fixtures/pairs.txt: offsets are 0-based in the API
and 1-based in the report.
"""

import verifylib

EXPECTED = [
    (1, "a", "c", 3, 6, "a=1;b"),
    (2, "x", "x", 1, "", "x=9"),
    (3, "alpha", "beta", 2, 15, "alpha"),
    (4, "z", "z", 1, "", "z="),
]

EXPECTED_SUMMARY = {"lines": 4, "pairs": 7}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "fields.csv",
        ["line", "first", "last", "pairs", "second_eq", "head"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
