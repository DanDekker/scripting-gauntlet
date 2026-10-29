"""Grader for 011-xml-attrs."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "products.csv",
        ["id", "name", "price", "tags"],
        [
            ("A-1", "Bolt", 0.50, "steel|small"),
            ("B-2", "Nut", 1.25, "steel"),
            ("C-3", "Screw", 0.75, ""),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"products": 3})
    return failures
