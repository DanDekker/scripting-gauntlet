"""Grader for 242-ps1-tryparse."""

import verifylib


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "readings.csv",
        ["name", "value"],
        [
            ("zero", 0),
            ("spaced", 17),
            ("negative", -3),
            ("padded", 5),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"accepted": 4, "rejected": 4, "total": 19},
    )
    return failures
