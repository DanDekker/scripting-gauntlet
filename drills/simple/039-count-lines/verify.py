"""Grader for 039-count-lines."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "linecounts.csv",
        ["file", "lines"],
        [
            ("app.log", 6),
            ("auth.log", 4),
            ("empty.log", 0),
            ("metrics.log", 3),
            ("worker.log", 6),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "total.json", {"files": 5, "lines": 19}
    )
    return failures
