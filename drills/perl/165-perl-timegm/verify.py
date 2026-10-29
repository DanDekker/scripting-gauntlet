"""Grader for 165-perl-timegm.

Expected epochs derived with python's calendar.timegm and verified against perl's
timegm; 5 valid stamps, 2 invalid.
"""

import verifylib

EXPECTED = [
    ("1970-01-01T00:00:00Z", 0),
    ("2024-02-29T00:00:00Z", 1709164800),
    ("2026-01-01T00:00:00Z", 1767225600),
    ("2026-10-29T12:00:00Z", 1793275200),
    ("2026-12-31T23:59:59Z", 1798761599),
]

EXPECTED_SUMMARY = {
    "lines": 7,
    "valid": 5,
    "invalid": 2,
    "first": 0,
    "last": 1798761599,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "epochs.csv", ["stamp", "epoch"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
