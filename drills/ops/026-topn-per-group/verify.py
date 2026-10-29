"""Grader for 026-topn-per-group."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "top2.csv",
        ["region", "rank", "rep", "revenue"],
        [
            ("east", 1, "Eli", 200.0),
            ("east", 2, "Fay", 200.0),
            ("north", 1, "Hal", 75.0),
            ("north", 2, "Ivy", 75.0),
            ("south", 1, "Kim", 500.0),
            ("west", 1, "Ben", 300.0),
            ("west", 2, "Ana", 120.5),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"regions": 4, "rows_in": 11, "rows_out": 7}
    )
    return failures
