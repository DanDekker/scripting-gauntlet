"""Grader for 107-backoff-plan."""

import verifylib

WAITS = [(1, 2), (2, 4), (3, 8), (4, 16)]
REQUESTS = [
    "POST /v1/chat 503",
    "GET /v1/models 429",
    "POST /v1/chat 500",
    "POST /v1/embed 504",
    "POST /v1/chat 503",
    "PATCH /v1/user 429",
]


def verify(io) -> list[str]:
    rows = [
        (request, attempt, wait)
        for request in REQUESTS
        for attempt, wait in WAITS
    ]
    failures = verifylib.table(io.out / "schedule.csv", ["request", "attempt", "wait_seconds"], rows)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "requests": 10,
            "success": 2,
            "retryable": 6,
            "client_errors": 2,
            "retries": 24,
            "exhausted": 6,
            "total_wait": 180,
        },
    )
    return failures
