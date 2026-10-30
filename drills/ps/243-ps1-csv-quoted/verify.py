"""Grader for 243-ps1-csv-quoted."""

import verifylib


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "invoices.csv",
        ["order_id", "customer", "units", "unit_price", "total"],
        [
            ("A-100", "Acme, Inc.", 2, 1.25, 2.50),
            ("A-101", "North Star", 1, 10.00, 10.00),
            ("A-102", "Solo", 0, 99.99, 0.00),
            ("A-103", "Edge", 3, 0.10, 0.30),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"orders": 4, "grand_total": 12.80, "zero_quantity": 1},
    )
    return failures
