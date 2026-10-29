"""Grader for 185-ps1-datetime.

Expected epochs derived with calendar.timegm: 3 April 2026 is 1775174400, and 31/02/2026
does not exist.
"""

import verifylib

EXPECTED = [
    (1, 1793275200),
    (2, 1767225600),
    (3, 1775174400),
    (4, 0),
]

EXPECTED_SUMMARY = {"rows": 4, "invalid": 1, "earliest": 0}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "epochs.csv", ["id", "epoch"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
