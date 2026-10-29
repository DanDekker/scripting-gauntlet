"""Grader for 081-manifest-drift."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "drift.csv",
        ["path", "change", "from_bytes", "to_bytes"],
        [
            ("api/routes/teams.py", "added", "", 640),
            ("api/routes/users.py", "changed", 1300, 1300),
            ("docs/old notes.md", "removed", 512, ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"added": 1, "removed": 1, "changed": 1, "unchanged": 3},
    )
    return failures
