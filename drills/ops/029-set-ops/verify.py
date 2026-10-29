"""Grader for 029-set-ops."""

import verifylib


def verify(io):
    failures = verifylib.lines(io.out / "union.txt", [f"u0{i}" for i in range(1, 8)])
    failures += verifylib.lines(io.out / "both.txt", ["u02", "u03"])
    failures += verifylib.lines(io.out / "only_a.txt", ["u01", "u05", "u07"])
    failures += verifylib.lines(io.out / "only_b.txt", ["u04", "u06"])
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"a": 5, "b": 4, "union": 7, "both": 2, "only_a": 3, "only_b": 2},
    )
    return failures
