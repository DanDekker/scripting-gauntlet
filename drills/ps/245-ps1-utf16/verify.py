"""Grader for 245-ps1-utf16."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "events.csv",
        ["level", "message"],
        [
            ("INFO", "job started"),
            ("WARN", "café cache low"),
            ("ERROR", "disk full"),
            ("INFO", "job done"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"records": 4, "info": 2, "warn": 1, "error": 1},
    )
    return failures
