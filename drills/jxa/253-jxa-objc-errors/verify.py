"""Grader for 253-jxa-objc-errors."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "checks.csv",
        ["id", "status", "bytes", "message"],
        [
            ("one", "ok", 6, ""),
            ("empty", "ok", 0, ""),
            ("missing", "missing", 0, "not found"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"jobs": 3, "ok": 2, "missing": 1, "bytes": 6},
    )
    return failures
