"""Grader for 023-filter-predicate."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "kept.csv",
        ["order_id", "customer", "region", "status", "amount"],
        [
            ("1001", "ACME", "west", "paid", 1250.0),
            ("1006", "Wayne", "west", "paid", 1200.0),
            ("1014", "Hooli", "west", "paid", 1000.0),
            ("1002", "Globex", "east", "paid", 300.0),
            ("1009", "Tyrell", "north", "paid", 250.5),
            ("1010", "Lumen", "east", "paid", 175.0),
            ("1008", "Wonka", "west", "paid", 100.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"rows_in": 14, "kept": 7, "dropped": 7, "total": 4275.5},
    )
    return failures
