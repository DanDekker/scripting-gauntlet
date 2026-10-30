"""Grader for 250-jxa-path-inventory."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "inventory.csv",
        ["path", "bytes", "kind"],
        [
            ("-dash.txt", 5, "file"),
            (".hidden", 7, "file"),
            ("reports/one.txt", 4, "file"),
            ("reports/two file.txt", 9, "file"),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"files": 4, "bytes": 25})
    return failures
