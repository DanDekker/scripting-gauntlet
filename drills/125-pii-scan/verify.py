"""Grader for 125-pii-scan."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "findings.csv",
        ["ticket", "line", "kind", "value"],
        [
            (1, 1, "email", "ada.lovelace@example.org"),
            (1, 1, "phone", "+1 (555) 010-2030"),
            (2, 2, "card", "4111 1111 1111 1111"),
            (4, 4, "ssn", "123-45-6789"),
            (5, 5, "private-ip", "10.2.3.4"),
            (6, 6, "private-ip", "192.168.1.20"),
            (6, 6, "private-ip", "172.20.5.9"),
            (7, 7, "phone", "555.010.2030"),
            (8, 8, "email", "support-555-010-2031@example.com"),
            (9, 9, "email", "555-010-2032@example.net"),
            (11, 11, "card", "3782 822463 10005"),
            (11, 11, "email", "bob@example.io"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "tickets": 11,
            "findings": 12,
            "by_kind": {"card": 2, "email": 4, "phone": 2, "private-ip": 3, "ssn": 1},
            "tickets_flagged": 9,
            "unique_values": 12,
        },
    )
    # The invalid-shaped values must never show up as findings.
    if (io.out / "findings.csv").is_file():
        _, rows = verifylib.read_csv(io.out / "findings.csv")
        values = {row[3] for row in rows if len(row) == 4}
        for bad in (
            "4111 1111 1111 1112",
            "000-12-3456",
            "666-12-3456",
            "123456789",
            "1234567890123456789012",
            "8.8.8.8",
            "172.40.5.9",
            "555-010-2031",
        ):
            if bad in values:
                failures.append(f"findings.csv: {bad!r} is not PII and must not be reported")
    return failures
