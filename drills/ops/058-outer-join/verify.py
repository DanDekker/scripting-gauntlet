"""Grader for 058-outer-join."""

import csv
import re
import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "joined.csv",
        ["sku", "name", "qty", "price", "side"],
        [
            ("a-100", "Widget", 5, 9.99, "both"),
            ("a-200", "Gadget", 0, "", "left"),
            ("b-300", "Doohickey", 12, 4.50, "both"),
            ("c-400", "Thing", 3, 7.25, "both"),
            ("d-500", "", "", 2.00, "right"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"keys": 5, "both": 3, "left_only": 1, "right_only": 1},
    )
    path = io.out / "joined.csv"
    if path.is_file():
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        for index, row in enumerate(rows[1:], start=1):
            if len(row) > 3 and row[3] and not re.fullmatch(r"-?\d+\.\d{2}", row[3]):
                failures.append(f"joined.csv row {index}: price must have two decimals")
    return failures
