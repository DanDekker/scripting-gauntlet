"""Grader for 056-network-events."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "actions.csv",
        ["action", "count"],
        [
            ("ALLOW", 7),
            ("DROP", 5),
            ("REJECT", 1),
        ],
    )
    failures += verifylib.table(
        io.out / "top_sources.csv",
        ["source", "attempts"],
        [
            ("10.0.0.5", 4),
            ("10.0.0.7", 3),
            ("10.0.0.9", 3),
            ("10.0.0.12", 2),
            ("10.0.0.11", 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"events": 13, "allowed": 7, "blocked": 6, "skipped": 1},
    )
    return failures
