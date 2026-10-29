"""Grader for 195-ps1-pipeline-unrolling.

Expected batches:
102 and 105 are single-item batches but MUST remain arrays (is_array == "true").
103 has 0 items but MUST remain an array.
"""

import verifylib

EXPECTED = [
    (101, 3, "true", "alpha"),
    (102, 1, "true", "solo"),
    (103, 0, "true", ""),
    (104, 2, "true", "one"),
    (105, 1, "true", "isolated"),
]

EXPECTED_SUMMARY = {
    "batches": 5,
    "total_items": 7,
    "single_item_batches": 2,
    "empty_batches": 1,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "batches.csv",
        ["id", "count", "is_array", "first"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
