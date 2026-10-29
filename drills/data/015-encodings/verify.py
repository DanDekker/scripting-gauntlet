"""Grader for 015-encodings."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "merged.csv",
        ["id", "source", "name", "city"],
        [
            (1, "utf8", "Zoë", "Montréal"),
            (2, "utf8bom", "Björn", "Stockholm"),
            (3, "utf16le", "Renée", "Lyon"),
            (4, "latin1", "Café", "Montréal"),
            (5, "crlf", "Ana", "Lisboa"),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"files": 5, "rows": 5})
    return failures
