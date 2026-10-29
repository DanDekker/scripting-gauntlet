"""Grader for 141-token-bucket."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "decisions.csv",
        ["id", "timestamp", "tokens", "status", "req_left", "tok_left"],
        [
            ("r1", 0, 900, "accept", "4.00", "100.00"),
            ("r3", 0, 120, "reject", "4.00", "100.00"),
            ("r7", 2, 500, "reject", "5.00", "300.00"),
            ("r2", 3, 60, "accept", "4.00", "340.00"),
            ("r8", 3, 40, "accept", "3.00", "300.00"),
            ("r5", 4, 950, "reject", "4.00", "400.00"),
            ("r4", 5, 100, "accept", "4.00", "400.00"),
            ("r12", 7, 0, "accept", "4.00", "600.00"),
            ("r13", 8, 1000, "reject", "5.00", "700.00"),
            ("r9", 9, 300, "accept", "4.00", "500.00"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_requests": 10,
            "accepted": 6,
            "rejected": 4,
            "tokens_served": 1400,
            "tokens_rejected": 2570,
        },
    )
    return failures
