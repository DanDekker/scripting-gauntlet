"""Grader for 033-percentiles."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "latency.csv",
        ["endpoint", "count", "p50", "p90", "max"],
        [
            ("/api/health", 1, 3, 3, 3),
            ("/api/orders", 5, 12, 40, 40),
            ("/api/users", 10, 30, 90, 300),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"endpoints": 3, "requests": 16, "slowest": 300}
    )
    return failures
