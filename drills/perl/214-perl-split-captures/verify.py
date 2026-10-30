"""Grader for 214-perl-split-captures.

Four access-log records; the 404 is the only non-2xx status.
"""

import verifylib

EXPECTED = [
    (1, "2026-10-29T10:00:00", "GET", "/health", "200"),
    (2, "2026-10-29T10:00:05", "POST", "/api/v1/orders", "201"),
    (3, "2026-10-29T10:00:09", "GET", "/missing", "404"),
    (4, "2026-10-29T10:00:14", "DELETE", "/api/v1/orders/7", "204"),
]

EXPECTED_SUMMARY = {"records": 4, "ok": 3, "errors": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "access.csv",
        ["index", "timestamp", "method", "path", "status"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
