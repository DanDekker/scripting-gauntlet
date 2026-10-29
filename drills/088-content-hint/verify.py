"""Grader for 088-content-hint."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "matches.csv",
        ["path", "line", "text"],
        [
            ("2026/march.md", 3, "The Quarterly Review   is scheduled for April 2"),
            ("misc.txt", 1, "the quarterly review is scheduled"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "match.json",
        {
            "path": "2026/march.md",
            "line": 3,
            "text": "The Quarterly Review   is scheduled for April 2",
        },
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files_scanned": 5, "matching_files": 2, "matching_lines": 2, "skipped_large": 1},
    )
    return failures
