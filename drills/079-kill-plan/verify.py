"""Grader for 079-kill-plan."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "plan.csv",
        ["pid", "signal", "command"],
        [
            (1337, "KILL", "python3"),
            (1500, "TERM", "reporter"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"candidates": 2, "kill": 1, "term": 1, "skipped": 2}
    )
    return failures
