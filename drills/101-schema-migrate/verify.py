"""Grader for 101-schema-migrate."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "changes.csv",
        ["property", "code"],
        [
            ("count", "now-required"),
            ("count", "type-changed"),
            ("display_name", "added"),
            ("email", "now-required"),
            ("legacy_flag", "removed"),
            ("meta", "now-optional"),
            ("nickname", "now-required"),
            ("notes", "type-changed"),
            ("tags", "added"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"breaking": 6, "safe": 3, "properties": 8},
    )
    return failures
