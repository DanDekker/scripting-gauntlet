"""Grader for 225-perl-die-message.

The reported message is the text from the fixture with no " at FILE line N." suffix.
"""

import verifylib

EXPECTED = [
    (1, "disk", "disk full"),
    (2, "net", "network unreachable"),
    (3, "mem", "out of memory"),
]

EXPECTED_SUMMARY = {"checks": 3, "longest": 19, "first": "disk full"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "checks.csv",
        ["index", "name", "message"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
