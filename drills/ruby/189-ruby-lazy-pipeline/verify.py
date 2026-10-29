"""Grader for 189-ruby-lazy-pipeline.

Expected matches: lines 2, 4, 5, 7, 8 (5 matches reached at line 8).
Inspected count must be 8, not 10!
"""

import verifylib

EXPECTED = [
    ("10:00:02", "WARN", 404, "not found"),
    ("10:00:04", "ERROR", 500, "timeout"),
    ("10:00:05", "WARN", 429, "rate limit"),
    ("10:00:07", "ERROR", 503, "unavailable"),
    ("10:00:08", "WARN", 400, "bad request"),
]

EXPECTED_SUMMARY = {"inspected": 8, "matched": 5, "target": 5}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "matches.csv",
        ["timestamp", "level", "code", "message"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
