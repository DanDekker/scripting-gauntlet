"""Grader for 130-rate-limit-headers."""

import verifylib

ROWS = [
    (200, 42, "", "proceed"),
    (429, 0, 30, "wait"),
    (429, 0, "", "wait-unknown"),
    (429, 0, 12, "wait"),
    (429, "", 60, "wait"),
    (200, 0, "", "hold"),
    (429, "", 0, "wait"),
    (200, 0, "", "hold"),
    (200, "", "", "proceed"),
    (429, 5, 0, "wait"),
    (429, 0, 0, "wait"),
]

SUMMARY = {"responses": 11, "skipped": 1, "blocked": 7, "exhausted": 2, "total_wait": 102}


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "responses.csv", ["status", "remaining", "wait", "action"], ROWS)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
