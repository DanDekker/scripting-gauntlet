"""Grader for 251-jxa-date-timezone."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "stamps.csv",
        ["id", "utc", "epoch"],
        [
            ("a", "2026-03-08T08:30:00Z", 1772958600),
            ("b", "2026-11-01T07:30:00Z", 1793518200),
            ("epoch", "1970-01-01T00:00:00Z", 0),
            ("offset", "2026-10-30T12:15:00Z", 1793362500),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"accepted": 4, "rejected": 1, "epoch_zero": 1},
    )
    return failures
