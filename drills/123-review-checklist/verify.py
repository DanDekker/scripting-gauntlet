"""Grader for 123-review-checklist."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "findings.csv",
        ["file", "line", "code"],
        [
            ("scripts/deploy.sh", 47, "hardcoded-endpoint"),
            ("scripts/deploy.sh", 48, "long-line"),
            ("scripts/deploy.sh", 49, "trailing-whitespace"),
            ("scripts/deploy.sh", 51, "trailing-whitespace"),
            ("scripts/deploy.sh", 52, "todo"),
            ("scripts/deploy.sh", 53, "debug"),
            ("src/api/client.js", 9, "hardcoded-endpoint"),
            ("src/api/client.js", 11, "todo"),
            ("src/api/client.js", 13, "debug"),
            ("src/util/parse.py", 35, "debug"),
            ("src/util/parse.py", 36, "trailing-whitespace"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files": 5,
            "lines_added": 22,
            "findings": 11,
            "by_code": {
                "debug": 3,
                "hardcoded-endpoint": 2,
                "long-line": 1,
                "todo": 2,
                "trailing-whitespace": 3,
            },
            "files_flagged": 3,
        },
    )
    return failures
