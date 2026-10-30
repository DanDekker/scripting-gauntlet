"""Grader for 204-perl-map-scalar-context.

Paid invoices: A1 120.50, A2 80.00, A4 310.75 -> total 511.25.
"""

import verifylib

EXPECTED_PAID = [
    ("A1", "120.50"),
    ("A2", "80.00"),
    ("A4", "310.75"),
]

EXPECTED_SUMMARY = {
    "invoices": 5,
    "paid_count": 3,
    "paid_total": 511.25,
    "unpaid_count": 2,
    "largest_paid_id": "A4",
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "paid.csv",
        ["id", "amount"],
        EXPECTED_PAID,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
