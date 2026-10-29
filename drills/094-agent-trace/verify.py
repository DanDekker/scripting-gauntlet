"""Grader for 094-agent-trace."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "tools.csv",
        ["tool", "calls", "errors", "tokens"],
        [
            ("bash", 2, 1, 650),
            ("edit_file", 1, 1, 75),
            ("grep", 3, 0, 400),
            ("read_file", 2, 0, 1200),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "turns": 8,
            "total_tokens": 2325,
            "cached_tokens": 1050,
            "error_turns": 2,
            "most_called_tool": "grep",
        },
    )
    return failures
