"""Grader for 246-ps1-literal-path."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "inventory.csv",
        ["path", "bytes", "first_line"],
        [
            ("-dash.txt", 13, "leading dash"),
            ("[plan].txt", 11, "draft plan"),
            ("*.log", 13, "literal star"),
            ("nested/notes.txt", 12, "nested note"),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"files": 4, "bytes": 49})
    return failures
