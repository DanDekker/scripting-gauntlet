"""Grader for 041-find-largest."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "sizes.csv",
        ["path", "bytes"],
        [
            ("logs/app/2026-09-30.log", 386),
            ("logs/edge/access.log", 374),
            ("logs/app/2026-10-01.log", 134),
            ("logs/edge/error.log", 134),
            ("reports/q3.md", 127),
            ("notes.txt", 77),
            ("reports/q3 draft.md", 58),
            ("README", 22),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "largest.json",
        {"files": 8, "bytes": 1312, "largest": "logs/app/2026-09-30.log"},
    )
    return failures
