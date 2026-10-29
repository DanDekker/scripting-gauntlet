"""Grader for 020-date-parsing."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "normalised.csv",
        ["id", "date"],
        [
            ("d1", "2026-03-05"),
            ("d2", "2026-03-05"),
            ("d3", "2025-12-31"),
            ("d4", "2026-03-05"),
            ("d5", "2026-03-05"),
            ("d6", "2026-03-05"),
            ("d7", "2026-03-05"),
            ("d8", "2026-01-02"),
            ("d9", ""),
            ("d10", ""),
            ("d11", ""),
            ("d12", "2025-12-25"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "rows": 12,
            "parsed": 9,
            "failed": 3,
            "earliest": "2025-12-25",
            "latest": "2026-03-05",
        },
    )
    return failures
