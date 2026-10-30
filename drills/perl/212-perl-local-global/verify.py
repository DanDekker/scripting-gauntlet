"""Grader for 212-perl-local-global.

The wide records use ';' and everything else uses ','; the separator setting is back
to ',' at the end.
"""

import verifylib

EXPECTED_LINES = [
    "plain,alpha",
    "wide;bravo",
    "plain,charlie",
    "wide;delta",
    "plain,epsilon",
]

EXPECTED_SUMMARY = {"records": 5, "wide": 2, "sep_after": ","}


def verify(io):
    failures = verifylib.lines(io.out / "report.txt", EXPECTED_LINES)
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
