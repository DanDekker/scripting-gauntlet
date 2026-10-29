"""Grader for 057-percent-of-group."""

import csv
import re
import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "shares.csv",
        ["region", "rep", "amount", "pct", "cum_pct"],
        [
            ("east", "alice", 50.0, 50.0, 50.0),
            ("east", "bob", 30.0, 30.0, 80.0),
            ("east", "cara", 20.0, 20.0, 100.0),
            ("north", "gus", 10.0, 33.33, 33.33),
            ("north", "hal", 10.0, 33.33, 66.67),
            ("north", "ivy", 10.0, 33.33, 100.0),
            ("west", "dan", 100.0, 40.0, 40.0),
            ("west", "eve", 100.0, 40.0, 80.0),
            ("west", "fay", 50.0, 20.0, 100.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"rows": 9, "groups": 3, "total": 380.0}
    )
    path = io.out / "shares.csv"
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        for index, row in enumerate(rows[1:], start=1):
            for column in (3, 4):
                if len(row) > column and not re.fullmatch(r"-?\d+\.\d{2}", row[column]):
                    failures.append(f"shares.csv row {index}: percentage must have two decimals")
    return failures
