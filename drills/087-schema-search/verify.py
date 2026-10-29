"""Grader for 087-schema-search."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "matches.csv",
        ["path", "delimiter", "columns", "rows"],
        [
            ("a/budget.csv", "comma", 3, 3),
            ("c/report.tsv", "tab", 4, 2),
            ("d/export.csv", "comma", 3, 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "found.json", {"path": "a/budget.csv", "rows": 3, "total": 1234.5}
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"files_scanned": 5, "matches": 3})
    return failures
