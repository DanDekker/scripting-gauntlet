"""Grader for 009-jsonl-stream."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "by_country.csv",
        ["country", "events", "revenue"],
        [
            ("US", 2, 130.0),
            ("CA", 3, 24.75),
        ],
    )
    failures += verifylib.table(
        io.out / "tags.csv",
        ["tag", "count"],
        [
            ("new", 2),
            ("red", 2),
            ("sale", 2),
            ("clearance", 1),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"events": 5, "users": 4})
    return failures
