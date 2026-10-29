"""Grader for 132-server-header-audit.

Expected values read by hand off fixtures/responses.txt: 11 blocks, 1 without a status
line, so 10 responses -> 1 redirect, 2 errors, 7 checked (3 pass, 4 fail) and 14 findings.
"""

import verifylib

ROWS = [
    ("/api/v1/items?page=2", 200, "Strict-Transport-Security", "missing"),
    ("/api/v1/items?page=2", 200, "X-Content-Type-Options", "missing"),
    ("/api/v1/items?page=2", 200, "Referrer-Policy", "missing"),
    ("/admin", 200, "Strict-Transport-Security", "weak"),
    ("/admin", 200, "Content-Security-Policy", "weak"),
    ("/admin", 200, "X-Content-Type-Options", "wrong-value"),
    ("/admin", 200, "X-Frame-Options", "wrong-value"),
    ("/admin", 200, "Referrer-Policy", "wrong-value"),
    ("/empty", 204, "Strict-Transport-Security", "missing"),
    ("/empty", 204, "Content-Security-Policy", "missing"),
    ("/empty", 204, "X-Content-Type-Options", "missing"),
    ("/empty", 204, "X-Frame-Options", "missing"),
    ("/empty", 204, "Referrer-Policy", "missing"),
    ("/api/status", 200, "Strict-Transport-Security", "weak"),
]

SUMMARY = {
    "responses": 10,
    "skipped": 1,
    "checked": 7,
    "pass": 3,
    "fail": 4,
    "redirect": 1,
    "error": 2,
    "findings": 14,
}


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "findings.csv", ["url", "status", "header", "reason"], ROWS
    )
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
