"""Grader for 190-ps1-exitcode-trap.

Expected results derived from steps.csv:
Steps 1, 3, 5 exit 0 (success)
Steps 2 (code 10) and 4 (code 42) exit non-zero (failed)
"""

import verifylib

EXPECTED = [
    (1, "ping", 0, "success"),
    (2, "fetch", 10, "failed"),
    (3, "auth", 0, "success"),
    (4, "sync", 42, "failed"),
    (5, "cleanup", 0, "success"),
]

EXPECTED_SUMMARY = {"total_steps": 5, "succeeded": 3, "failed": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "results.csv",
        ["id", "action", "code", "status"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
