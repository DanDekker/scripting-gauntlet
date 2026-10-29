"""Grader for 073-http-pagination."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "items.csv",
        ["id", "name"],
        [
            (1, "alpha"),
            (2, "beta"),
            (3, "gamma"),
            (4, "delta"),
            (5, "epsilon"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"pages": 3, "items": 5, "duplicates": 1}
    )
    return failures
