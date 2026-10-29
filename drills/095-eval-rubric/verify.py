"""Grader for 095-eval-rubric."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "scores.csv",
        ["id", "kind", "passed"],
        [
            ("c1", "exact", "true"),
            ("c2", "exact", "false"),
            ("c3", "contains", "true"),
            ("c4", "number", "true"),
            ("c5", "number", "false"),
            ("c6", "regex", "false"),
            ("c7", "number", "false"),
            ("c8", "exact", "true"),
            ("c9", "contains", "false"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"total": 9, "passed": 4, "failed": 5, "pass_rate": 0.4444},
    )
    return failures
