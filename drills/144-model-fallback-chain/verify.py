"""Grader for 144-model-fallback-chain."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "resolutions.csv",
        ["task_id", "outcome", "resolved_tier", "attempts_count", "total_latency_ms"],
        [
            ("t1", "success", "1", 1, 800),
            ("t2", "success", "1", 2, 2100),
            ("t3", "success", "2", 4, 6300),
            ("t4", "success", "1", 2, 4400),
            ("t5", "failed", "", 0, 0),
            ("t6", "failed", "", 5, 3610),
            ("t7", "success", "1", 1, 2000),
            ("t8", "success", "3", 5, 4600),
            ("t9", "success", "2", 2, 1250),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_tasks": 9,
            "success_count": 7,
            "failed_count": 2,
            "fallback_invoked": 3,
            "total_latency_ms": 25060,
        },
    )
    return failures
