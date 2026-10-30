"""Grader for 249-jxa-file-io."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "lines.csv",
        ["index", "text", "chars", "bytes"],
        [
            (1, "alpha", 5, 5),
            (2, "βeta", 4, 5),
            (3, "café 😀", 6, 10),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"records": 3, "chars": 15, "bytes": 20},
    )
    return failures
