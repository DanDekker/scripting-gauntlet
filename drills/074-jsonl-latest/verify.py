"""Grader for 074-jsonl-latest."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "latest.csv",
        ["id", "ts", "status"],
        [
            ("a1", "2026-02-01T12:30:00Z", "done"),
            ("b2", "2026-02-01T09:00:00Z", "retry"),
            ("c3", "2026-02-01T11:00:00Z", "new"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"records": 6, "ids": 3, "dropped": 3}
    )
    return failures
