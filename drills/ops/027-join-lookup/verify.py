"""Grader for 027-join-lookup."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "enriched.csv",
        ["order_id", "customer_id", "name", "country", "amount"],
        [
            ("1001", "c-01", "Acme", "US", 120.0),
            ("1002", "c-02", "Beta Corp Ltd", "CA", 80.5),
            ("1003", "c-99", "UNKNOWN", "??", 45.0),
            ("1004", "c-03", "Gamma", "DE", 200.0),
            ("1005", "", "UNKNOWN", "??", 15.0),
            ("1006", "c-01", "Acme", "US", 60.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"orders": 6, "matched": 4, "unmatched": 2, "total": 520.5},
    )
    return failures
