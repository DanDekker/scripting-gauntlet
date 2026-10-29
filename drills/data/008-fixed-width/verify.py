"""Grader for 008-fixed-width."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "inventory.csv",
        ["name", "dept", "qty", "price", "total"],
        [
            ("ALICE", "SALES", 12, 125.50, 1506.00),
            ("BOB", "ENG", 3, 1000.00, 3000.00),
            ("CAROL", "OPS", 47, 89.99, 4229.53),
            ("DAVE", "ENG", 0, 2500.00, 0.00),
            ("", "MKT", 7, 15.00, 105.00),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"records": 5, "blank_names": 1})
    return failures
