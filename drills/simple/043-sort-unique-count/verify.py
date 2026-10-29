"""Grader for 043-sort-unique-count."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "levels.csv",
        ["level", "count"],
        [
            ("INFO", 8),
            ("ERROR", 5),
            ("WARN", 3),
            ("DEBUG", 2),
            ("TRACE", 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"lines": 19, "levels": 5, "top": "INFO"}
    )
    return failures
