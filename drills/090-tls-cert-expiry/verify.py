"""Grader for 090-tls-cert-expiry."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "certs.csv",
        ["cn", "not_after", "status"],
        [
            ("api.old.org", "2026-10-20T00:00:00Z", "expired"),
            ("*.example.com", "2026-11-10T00:00:00Z", "warning"),
            ("common.net", "2027-01-01T00:00:00Z", "ok"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "coverage.json",
        {
            "audit_time": "2026-10-29T12:00:00Z",
            "total_certs": 3,
            "expired_count": 1,
            "warning_count": 1,
            "ok_count": 1,
            "uncovered_targets": [
                "api.old.org",
                "sub.app.example.com",
                "example.com",
                "admin.common.net",
                "missing.org",
            ],
        },
    )
    return failures
