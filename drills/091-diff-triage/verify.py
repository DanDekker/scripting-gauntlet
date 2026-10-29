"""Grader for 091-diff-triage."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "risk.csv",
        ["path", "added", "deleted", "flags"],
        [
            ("assets/logo.png", 0, 0, "binary;new"),
            ("config/settings.ini", 1, 1, "mode-change"),
            ("docs/readme.md", 1, 1, ""),
            ("src/app.py", 4, 1, "secret"),
            ("src/legacy.py", 0, 2, "deleted"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files": 5,
            "total_added": 6,
            "total_deleted": 5,
            "flagged_files": 4,
            "top_risk": "assets/logo.png",
        },
    )
    return failures
