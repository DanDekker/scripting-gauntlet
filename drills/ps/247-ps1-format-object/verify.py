"""Grader for 247-ps1-format-object."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "report.csv",
        ["name", "status", "latency_ms", "owner", "healthy"],
        [
            ("api", "up", 12, "platform", "yes"),
            ("worker", "down", 0, "jobs", "no"),
            ("web", "up", 120, "frontend", "no"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"services": 3, "healthy": 1, "down": 1, "slow": 1},
    )
    return failures
