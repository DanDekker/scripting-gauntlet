"""Grader for 234-perl-jsonl-filter.

Verifies service event aggregation and error-count sorting.
"""

import verifylib

EXPECTED = [
    ("payment", 3, 2, 450, 150.0),
    ("auth", 3, 1, 180, 60.0),
    ("catalog", 2, 1, 485, 242.5),
]

EXPECTED_SUMMARY = {
    "total_events": 8,
    "total_errors": 4,
    "total_duration_ms": 1115,
    "services_count": 3,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "services.csv",
        ["service", "events", "errors", "total_duration_ms", "avg_duration_ms"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
