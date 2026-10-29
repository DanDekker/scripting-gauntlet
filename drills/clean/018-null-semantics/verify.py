"""Grader for 018-null-semantics."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "clean.csv",
        ["id", "name", "email", "age"],
        [
            ("1", "Alice", "alice@example.com", 30),
            ("2", "Bob", "", ""),
            ("3", "Cara", "", ""),
            ("4", "Dave", "dave@example.com", 0),
            ("5", "Eve", "", ""),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"rows": 5, "nulls": 6})
    return failures
