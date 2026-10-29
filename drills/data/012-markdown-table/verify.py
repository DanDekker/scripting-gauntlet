"""Grader for 012-markdown-table."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "table.csv",
        ["region", "qty", "revenue"],
        [
            ("North", 10, 1250.00),
            ("South", 4, 980.50),
            ("North", 3, 310.25),
            ("East", 7, 610.00),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"rows": 4, "total_qty": 24, "total_revenue": 3150.75}
    )
    return failures
