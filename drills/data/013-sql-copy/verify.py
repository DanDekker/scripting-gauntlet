"""Grader for 013-sql-copy."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "orders.csv",
        ["id", "customer", "region", "amount"],
        [
            ("1", "ACME", "North", 1250.00),
            ("2", "GLOBEX", "South", 980.50),
            ("3", "ACME", "North", 310.25),
            ("4", "INITECH", "East", 610.00),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"rows": 4, "total": 3150.75})
    return failures
