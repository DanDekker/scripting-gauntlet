"""Grader for 105-repo-map."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "map.csv",
        ["kind", "files", "bytes"],
        [
            ("config", 2, 58),
            ("js", 2, 51),
            ("md", 3, 96),
            ("other", 5, 118),
            ("py", 3, 80),
            ("test", 2, 62),
            ("ts", 1, 28),
        ],
    )
    failures += verifylib.table(
        io.out / "dirs.csv",
        ["dir", "files"],
        [
            ("(root)", 4),
            (".github", 1),
            ("docs", 3),
            ("scripts", 2),
            ("src", 5),
            ("web", 3),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files": 18, "bytes": 493, "skipped": 3, "dirs": 6, "largest": 50},
    )
    return failures
