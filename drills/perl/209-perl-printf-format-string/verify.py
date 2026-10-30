"""Grader for 209-perl-printf-format-string.

Templates are copied verbatim: "Deploy: 100% complete" keeps its percent sign and
the text after it.
"""

import verifylib

EXPECTED_LINES = [
    "Deploy: 100% complete",
    "Disk: 85% full",
    "Queue: 0 pending",
]

EXPECTED_SUMMARY = {"templates": 3, "percent_templates": 2, "chars": 51}


def verify(io):
    failures = verifylib.lines(io.out / "report.txt", EXPECTED_LINES)
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
