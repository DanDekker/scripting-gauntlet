"""Grader for 134-cost-allocation."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "projects.csv",
        ["project", "turns", "cost", "budget", "over_budget"],
        [
            ("data-platform", 1, "0.0180", "0.0100", "true"),
            ("frontend", 3, "0.0128", "5.0000", "false"),
            ("infra", 8, "0.1320", "10.0000", "false"),
            ("research", 1, "0.0000", "", "false"),
        ],
    )
    failures += verifylib.table(
        io.out / "roles.csv",
        ["role", "turns", "cost", "pct_spend"],
        [
            ("coder", 5, "0.0878", "53.93"),
            ("planner", 7, "0.0570", "35.01"),
            ("reviewer", 1, "0.0180", "11.06"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_turns": 17,
            "valid_turns": 13,
            "unpriced_turns": 2,
            "total_spend": 0.1628,
            "over_budget_projects": 1,
            "successful_sessions": 8,
            "total_sessions": 11,
        },
    )
    return failures

