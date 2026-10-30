"""Grader for 255-tcl-split-fields."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "records.csv",
        ["id", "name", "tag", "tag_state"],
        [
            ("1", "Alpha", "", "empty"),
            ("2", "Beta", "x", "value"),
            ("3", "", "y", "value"),
            ("4", "Gamma", "", "empty"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"records": 4, "empty_tag": 2, "blank_name": 1},
    )
    return failures
