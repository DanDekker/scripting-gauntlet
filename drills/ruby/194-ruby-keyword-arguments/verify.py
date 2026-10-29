"""Grader for 194-ruby-keyword-arguments.

Expected endpoints derived from endpoints.json:
3: metrics.internal with explicit null path and timeout -> url without trailing slash, empty timeout
5: missing_host
"""

import verifylib

EXPECTED = [
    (1, "valid", "http://api.internal:9000/v1", "15"),
    (2, "valid", "http://auth.internal:8080/", "30"),
    (3, "valid", "http://metrics.internal:8080", ""),
    (4, "valid", "http://db.internal:5432/", "60"),
    (5, "missing_host", "", ""),
]

EXPECTED_SUMMARY = {"endpoints": 5, "valid": 4, "missing_host": 1, "null_overrides": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "endpoints.csv",
        ["id", "status", "url", "timeout"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
