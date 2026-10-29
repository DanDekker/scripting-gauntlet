"""Grader for 007-quoted-fields."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "clean.csv",
        ["id", "note", "amount"],
        [
            ("1", "Hello, world", 10),
            ("2", 'She said "hi"', 20),
            ("3", "line one\nline two", 30),
            ("4", "plain", 40),
        ],
    )
    failures += verifylib.json_eq(io.out / "stats.json", {"rows": 4, "multiline": 1})
    return failures
