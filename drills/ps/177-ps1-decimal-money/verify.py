"""Grader for 177-ps1-decimal-money.

Expected values derived by hand from fixtures/amounts.csv: decimal sums, half away from
zero at two decimals, three accounts sitting on a half cent.
"""

import verifylib

EXPECTED = [
    ("alice", "10.15", 2),
    ("bob", "0.20", 1),
    ("carol", "1.01", 1),
    ("dave", "2.68", 1),
    ("eve", "0.30", 2),
    ("frank", "1.01", 2),
]

EXPECTED_SUMMARY = {"accounts": 6, "total": "15.35", "half_cents": 3}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "totals.csv", ["account", "total", "items"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
