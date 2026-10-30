"""Grader for 260-tcl-catch-expr."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "ratios.csv",
        ["id", "ratio"],
        [("whole", "5.00"), ("negative", "-3.50")],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"accepted": 2, "rejected": 2},
    )
    return failures
