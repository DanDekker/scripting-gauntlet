"""Grader for 014-logfmt."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "requests.csv",
        ["path", "status", "dur_ms"],
        [
            ("/api/orders", 504, 3000),
            ("/api/search", 200, 800),
            ("/api/search", 200, 12),
            ("/api/users", 200, 12),
            ("/api/users", 200, 9),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"lines": 5, "errors": 1, "warns": 1, "infos": 3}
    )
    return failures
