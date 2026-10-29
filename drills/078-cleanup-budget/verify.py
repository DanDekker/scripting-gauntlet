"""Grader for 078-cleanup-budget."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "cleanup.csv",
        ["order", "path", "size_mb", "risk"],
        [
            (1, "/var/cache/apt", 1500, 1),
            (2, "/var/log/journal", 900, 1),
            (3, "/var/cache/pip", 800, 1),
            (4, "/home/pp/.cache", 400, 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"target_mb": 3500, "freed_mb": 3600, "taken": 4, "complete": True},
    )
    return failures
