"""Grader for 032-running-total."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "running.csv",
        ["account", "date", "amount", "balance"],
        [
            ("a1", "2026-01-03", 100.0, 100.0),
            ("a1", "2026-01-03", -30.0, 70.0),
            ("a1", "2026-01-05", 10.0, 80.0),
            ("a1", "2026-01-07", 5.5, 85.5),
            ("b2", "2026-01-02", 40.0, 40.0),
            ("b2", "2026-01-06", -40.0, 0.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"accounts": 2, "transactions": 6, "net": 85.5}
    )
    return failures
