"""Grader for 047-orphan-check."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "orphans.csv",
        ["child_file", "child_row", "column", "key_value", "parent_file"],
        [
            ("items.csv", 4, "order_id", "5099", "orders.csv"),
            ("orders.csv", 4, "customer_id", "9", "customers.csv"),
            ("orders.csv", 7, "customer_id", "7", "customers.csv"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"customers": 4, "orders": 7, "items": 4, "orphan_orders": 2, "orphan_items": 1, "orphan_rows": 3},
    )
    return failures
