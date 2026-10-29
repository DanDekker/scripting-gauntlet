"""Grader for 025-groupby-aggregate."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "rollup.csv",
        ["region", "month", "orders", "revenue", "avg_order"],
        [
            ("east", "2026-02", 2, 300.0, 150.0),
            ("north", "2026-02", 1, 50.25, 50.25),
            ("north", "2026-03", 1, 49.75, 49.75),
            ("west", "2026-01", 3, 300.0, 100.0),
            ("west", "2026-03", 1, 10.0, 10.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"rows_in": 9, "skipped": 1, "groups": 5, "revenue": 710.0},
    )
    return failures
