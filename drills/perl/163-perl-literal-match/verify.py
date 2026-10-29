"""Grader for 163-perl-literal-match.

Expected values derived from fixtures/queries.txt by hand and cross-checked against the
perl and python references.
"""

import verifylib

EXPECTED = [
    ("a.b", 0, "", 0),
    ("a.b", 1, 2, 1),
    ("00%", 1, 2, 1),
    ("x*y", 0, "", 0),
    ("a(b", 1, 4, 1),
    ("aa", 1, 1, 1),
]

EXPECTED_SUMMARY = {"lines": 6, "matched": 4, "invalid": 0}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "matches.csv",
        ["pattern", "found", "position", "count"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
