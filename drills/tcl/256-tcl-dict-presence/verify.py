"""Grader for 256-tcl-dict-presence."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "settings.csv",
        ["key", "state", "value"],
        [
            ("limit", "zero", "0"),
            ("owner", "empty", ""),
            ("enabled", "value", "false"),
            ("region", "missing", ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"keys": 4, "missing": 1, "empty": 1, "zero": 1},
    )
    return failures
