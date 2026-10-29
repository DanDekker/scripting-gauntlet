"""Grader for 200-ps1-regex-groups.

Expected output: lines 2 and 4 must NOT leak IDs from lines 1 and 3.
"""

import verifylib

EXPECTED = [
    (1, 101, "SUCCESS", 42, "true"),
    (2, "", "", "", "false"),
    (3, 102, "FAILED", 120, "true"),
    (4, "", "", "", "false"),
    (5, 103, "SUCCESS", 15, "true"),
]

EXPECTED_SUMMARY = {
    "total_lines": 5,
    "valid_records": 3,
    "corrupt_lines": 2,
    "avg_duration": 59,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "parsed.csv",
        ["step", "id", "status", "duration", "valid"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
