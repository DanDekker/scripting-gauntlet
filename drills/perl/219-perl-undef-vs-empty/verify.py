"""Grader for 219-perl-undef-vs-empty.

host is set, port is set, timeout is present-but-empty, retries is absent entirely.
"""

import verifylib

EXPECTED = [
    (1, "host", "set", "db.local"),
    (2, "port", "set", "5432"),
    (3, "timeout", "empty", ""),
    (4, "retries", "missing", ""),
]

EXPECTED_SUMMARY = {"wanted": 4, "set": 2, "empty": 1, "missing": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "settings.csv",
        ["index", "key", "status", "value"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
