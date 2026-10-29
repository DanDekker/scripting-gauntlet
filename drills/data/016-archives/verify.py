"""Grader for 016-archives."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "by_region.csv",
        ["region", "amount", "rows"],
        [
            ("South", 250.00, 2),
            ("North", 200.00, 3),
            ("East", 30.00, 1),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"files": 2, "rows": 6})
    return failures
