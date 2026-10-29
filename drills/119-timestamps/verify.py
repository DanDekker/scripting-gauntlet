"""Grader for 119-timestamps."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "entries.csv",
        ["timestamp", "message"],
        [
            ("1938-04-24T22:13:20Z", "negative epoch"),
            ("1970-01-01T00:00:00Z", "epoch zero"),
            ("2026-01-01T00:00:00Z", "epoch new year"),
            ("2026-10-09T12:00:00Z", "single-digit day"),
            ("2026-10-28T23:30:00Z", "slash date"),
            ("2026-10-29T09:00:00Z", "naive utc marker"),
            ("2026-10-29T10:00:00Z", "another entry"),
            ("2026-10-29T12:00:00Z", "boot complete"),
            ("2026-10-29T12:00:00Z", "regional cutover"),
            ("2026-10-29T12:00:00Z", "syslog line"),
            ("2026-10-29T12:00:00Z", "fractional seconds"),
            ("2026-10-29T12:00:00Z", "with comma, in the message"),
            ("2026-10-29T12:00:05Z", "lowercase month"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "lines": 17,
            "parsed": 13,
            "skipped": 4,
            "first": "1938-04-24T22:13:20Z",
            "last": "2026-10-29T12:00:05Z",
        },
    )
    return failures
