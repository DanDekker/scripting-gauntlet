"""Grader for 111-session-handoff."""

import verifylib


def verify(io) -> list[str]:
    return verifylib.json_eq(
        io.out / "handoff.json",
        {
            "request": "also update the docs and the changelog",
            "tools": ["read_file", "grep", "write_file", "run_tests"],
            "results": 3,
            "notes": [
                "the parser drops trailing whitespace",
                "retry after fixing the fixture",
            ],
            "errors": [
                "TimeoutError after 30s",
                "AssertionError: expected 41 got 42",
            ],
            "calls": 4,
            "unresolved": 1,
        },
    )
