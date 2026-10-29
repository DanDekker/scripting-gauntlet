"""Grader for 193-perl-regex-lookaround.

Expected values derived from stream.txt:
4 currencies: USD 150, EUR 40, GBP 300, USD 250
5 motifs:
  MOTIF104: ABA at 1, ABA at 3
  MOTIF105: XAX at 1, XAX at 3, XAX at 5
Total: 9 records.
"""

import verifylib

EXPECTED = [
    ("AUDIT101", "currency", "USD", 150),
    ("AUDIT101", "currency", "EUR", 40),
    ("AUDIT103", "currency", "GBP", 300),
    ("AUDIT103", "currency", "USD", 250),
    ("MOTIF104", "motif", "ABA", 1),
    ("MOTIF104", "motif", "ABA", 3),
    ("MOTIF105", "motif", "XAX", 1),
    ("MOTIF105", "motif", "XAX", 3),
    ("MOTIF105", "motif", "XAX", 5),
]

EXPECTED_SUMMARY = {"records": 9, "currencies": 4, "motifs": 5}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "extractions.csv",
        ["id", "type", "key", "val"],
        EXPECTED,
        key_count=2,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
