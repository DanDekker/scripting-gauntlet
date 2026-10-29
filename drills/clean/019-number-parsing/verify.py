"""Grader for 019-number-parsing."""

import csv
import re
import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "parsed.csv",
        ["id", "value"],
        [
            ("A1", 1234.50),
            ("A2", 42.0),
            ("A3", -89.99),
            ("A4", 12.5),
            ("A5", 1500.0),
            ("A6", 7.0),
            ("A7", 250.0),
            ("A8", ""),
            ("A9", -0.5),
            ("A10", 1000.0),
            ("A11", 0.25),
            ("A12", ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"rows": 12, "parsed": 10, "failed": 2, "total": 3955.76},
    )
    path = io.out / "parsed.csv"
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        for index, row in enumerate(rows[1:], start=1):
            if len(row) > 1 and row[1] and not re.fullmatch(r"-?\d+\.\d{2}", row[1]):
                failures.append(f"parsed.csv row {index}: value must have two decimals")
    return failures
