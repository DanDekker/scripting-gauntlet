"""Grader for 093-context-budget."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.lines(
        io.out / "context.txt",
        [
            "docs/api.md",
            "src/util.py",
            "tests/test_main.py",
            "assets/logo.png",
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"budget": 400, "included": 4, "included_tokens": 390, "skipped": 1, "remaining": 10},
    )
    return failures
