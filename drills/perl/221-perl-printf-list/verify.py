"""Grader for 221-perl-printf-list.

Three records means three lines in the report; a printf that takes the whole list as
arguments writes one line and warns.
"""

import verifylib

EXPECTED_LINES = ["alpha", "bravo", "charlie"]

EXPECTED_SUMMARY = {"records": 3, "lines": 3, "last": "charlie"}


def verify(io):
    failures = verifylib.lines(io.out / "report.txt", EXPECTED_LINES)
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
