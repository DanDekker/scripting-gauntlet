"""Grader for 086-fuzzy-find."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "candidates.csv",
        ["path", "score"],
        [
            ("home/pp/Downloads/march-budget-final.csv", 2),
            ("home/pp/Downloads/budget-march-v2.csv", 2),
            ("home/pp/Desktop/march-budget.csv", 2),
            ("home/pp/Downloads/spreadsheet-march.csv", 2),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "found.json",
        {
            "path": "home/pp/Downloads/march-budget-final.csv",
            "score": 2,
            "rows": 3,
            "total": 425.75,
        },
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"scanned": 7, "candidates": 4})
    return failures
