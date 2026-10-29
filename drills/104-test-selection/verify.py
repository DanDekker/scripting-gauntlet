"""Grader for 104-test-selection."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.lines(
        io.out / "selected.txt",
        ["tests/cli.py", "tests/metrics.py", "tests/parser.py", "tests/report.py"],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"changes": 4, "known": 2, "unknown": 2, "tests": 6, "selected": 4, "unused": 2},
    )
    return failures
