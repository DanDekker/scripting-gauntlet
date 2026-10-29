"""Grader for 122-agent-memory."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "memory.csv",
        ["key", "value", "ts"],
        [
            ("deploy.target", "staging", 1767225900),
            ("build.branch", "", 1767225800),
            ("user.name", "Ada L.", 1767225000),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "observations": 11,
            "expired": 2,
            "conflicts": 3,
            "stored": 3,
            "evicted": 3,
            "keys": ["build.branch", "deploy.target", "user.name"],
        },
    )
    return failures
