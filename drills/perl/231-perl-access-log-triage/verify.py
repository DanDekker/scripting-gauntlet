"""Grader for 231-perl-access-log-triage.

Verifies IP traffic rollup and status code categorization.
"""

import verifylib

EXPECTED = [
    ("10.0.0.5", 3, 664),
    ("192.168.1.10", 3, 57),
    ("192.168.1.20", 2, 42),
]

EXPECTED_SUMMARY = {
    "requests": 8,
    "total_bytes": 763,
    "s2xx": 4,
    "s3xx": 1,
    "s4xx": 2,
    "s5xx": 1,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "clients.csv",
        ["ip", "requests", "bytes"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
