"""Grader for 198-perl-state-variables.

Expected streaks and alerts (threshold 3):
Step 5: auth reaches 3 failures -> alert!
Step 8: api reaches 3 failures -> alert!
"""

import verifylib

EXPECTED = [
    (1, "10:00:01", "api", "OK", 0, "false"),
    (2, "10:00:02", "auth", "FAIL", 1, "false"),
    (3, "10:00:03", "auth", "FAIL", 2, "false"),
    (4, "10:00:04", "api", "FAIL", 1, "false"),
    (5, "10:00:05", "auth", "FAIL", 3, "true"),
    (6, "10:00:06", "auth", "OK", 0, "false"),
    (7, "10:00:07", "api", "FAIL", 2, "false"),
    (8, "10:00:08", "api", "FAIL", 3, "true"),
    (9, "10:00:09", "auth", "FAIL", 1, "false"),
]

EXPECTED_SUMMARY = {"checks": 9, "alerts": 2, "max_streak": 3}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "streaks.csv",
        ["step", "timestamp", "service", "status", "streak", "alert"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
