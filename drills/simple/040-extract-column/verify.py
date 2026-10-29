"""Grader for 040-extract-column."""

import verifylib


def verify(io):
    failures = verifylib.lines(
        io.out / "hosts.txt",
        ["web-01", "web-02", "db-01", "web-09", "cache-1", "edge-02"],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"rows": 6, "skipped": 2})
    return failures
