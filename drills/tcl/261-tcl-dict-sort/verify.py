"""Grader for 261-tcl-dict-sort."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "counts.csv",
        ["key", "count"],
        [("api", 4), ("cache", 2), ("web", 2)],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"keys": 3, "total": 8})
    return failures
