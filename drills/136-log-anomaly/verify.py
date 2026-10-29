"""Grader for 136-log-anomaly."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "anomalies.csv",
        ["minute", "requests", "errors", "error_rate", "baseline_rate", "culprit"],
        [
            ("2026-10-29T10:05:00Z", 100, 20, "0.2000", "0.0300", "TimeoutError"),
            ("2026-10-29T10:08:00Z", 100, 40, "0.4000", "0.0680", "RateLimitError"),
            ("2026-10-29T10:14:00Z", 100, 30, "0.3000", "0.0324", "Unknown"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_minutes": 18,
            "evaluated_minutes": 11,
            "anomaly_minutes": 3,
            "top_culprit": "RateLimitError",
        },
    )
    return failures
