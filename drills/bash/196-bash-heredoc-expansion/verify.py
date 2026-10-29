"""Grader for 196-bash-heredoc-expansion.

Expected runner outputs:
api start: Starting api in prod on port 8080...
api check: Checking health at http://127.0.0.1:8080/healthz
auth start: Starting auth in staging on port 9000...
auth check: Checking health at http://127.0.0.1:9000/status
worker start: Starting worker in prod on port 5000...
worker check: Checking health at http://127.0.0.1:5000/ping
"""

import verifylib

EXPECTED = [
    ("api", "start", 0, "Starting api in prod on port 8080..."),
    ("api", "check", 0, "Checking health at http://127.0.0.1:8080/healthz"),
    ("auth", "start", 0, "Starting auth in staging on port 9000..."),
    ("auth", "check", 0, "Checking health at http://127.0.0.1:9000/status"),
    ("worker", "start", 0, "Starting worker in prod on port 5000..."),
    ("worker", "check", 0, "Checking health at http://127.0.0.1:5000/ping"),
]

EXPECTED_SUMMARY = {"services": 3, "total_runs": 6, "success": 6}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "manifest.csv",
        ["service", "action", "exit_code", "output"],
        EXPECTED,
        key_count=2,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
