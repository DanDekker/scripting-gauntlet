"""Grader for 021-unicode-normalize."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "normalised.csv",
        ["id", "key"],
        [
            ("n1", "cafe"),
            ("n2", "cafe"),
            ("n3", "strasse"),
            ("n4", "strasse"),
            ("n5", "jose alvarez"),
            ("n6", "jose alvarez"),
            ("n7", "istanbul"),
            ("n8", "cafe"),
            ("n9", "lisbon"),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"rows": 9, "distinct": 5})
    return failures
