"""Grader for 223-perl-list-repetition.

Three rows of "alpha beta" (10 characters each): three lines, 30 characters.
"""

import verifylib

EXPECTED_LINES = ["alpha beta", "alpha beta", "alpha beta"]

EXPECTED_SUMMARY = {"count": 3, "lines": 3, "chars": 30}


def verify(io):
    failures = verifylib.lines(io.out / "report.txt", EXPECTED_LINES)
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
