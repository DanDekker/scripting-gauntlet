"""Grader for 099-flaky-detect."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "flaky.csv",
        ["test", "total", "passed", "failed", "fail_rate"],
        [
            ("test_checkout", 5, 2, 3, 0.6),
            ("test_login", 5, 3, 2, 0.4),
            ("test_upload", 3, 2, 1, 0.3333),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"tests": 7, "flaky": 3, "stable_pass": 2, "stable_fail": 2, "runs": 21},
    )
    return failures
