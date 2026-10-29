"""Grader for 197-lua-coroutine-filter.

Expected cumulative sums and alert triggers (threshold 50):
A reaches 55 at step 5 (alert)
B reaches 65 at step 6 (alert)
A reaches 60 at step 7 (alert)
"""

import verifylib

EXPECTED = [
    (1, "A", 10, 10, "false"),
    (2, "B", 20, 20, "false"),
    (3, "A", 25, 35, "false"),
    (4, "B", 15, 35, "false"),
    (5, "A", 20, 55, "true"),
    (6, "B", 30, 65, "true"),
    (7, "A", 5, 60, "true"),
]

EXPECTED_SUMMARY = {"events": 7, "streams": 2, "alerts": 3, "final_max": 65}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "meter.csv",
        ["step", "stream", "delta", "sum", "alert"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
