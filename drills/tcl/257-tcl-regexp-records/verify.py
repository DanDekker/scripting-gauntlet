"""Grader for 257-tcl-regexp-records."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "events.csv",
        ["level", "worker", "duration", "slow"],
        [
            ("INFO", "api.v2", 12, "no"),
            ("WARN", "web", 0, "no"),
            ("ERROR", "db", 305, "yes"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"records": 3, "skipped": 1, "slow": 1},
    )
    return failures
