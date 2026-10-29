"""Grader for 010-json-flatten."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "flat.csv",
        ["sku", "name", "price", "material", "weight", "tags"],
        [
            ("A-1", "Bolt", 0.50, "steel", 12, "steel|small"),
            ("B-2", "Nut", 1.25, "steel", 8, "steel|small"),
            ("C-3", "Screw", 0.75, "brass", 3, "small"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "meta.json", {"generated": "2026-10-01", "count": 3}
    )
    return failures
