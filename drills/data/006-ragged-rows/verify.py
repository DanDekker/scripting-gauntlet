"""Grader for 006-ragged-rows."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "clean.csv",
        ["id", "name", "city", "amount"],
        [
            ("1", "Alice", "Edmonton", 100),
            ("2", "Bob", "Calgary", ""),
            ("3", "Cara", "Vancouver", 300),
            ("4", "Dave", "Red Deer", 250),
            ("5", "Eve", "", 175),
            ("6", "Frank", "Halifax", 90),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"rows": 6, "padded": 1, "truncated": 2}
    )
    return failures
