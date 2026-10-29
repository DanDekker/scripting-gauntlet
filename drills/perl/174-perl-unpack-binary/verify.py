"""Grader for 174-perl-unpack-binary.

Expected values derived from the fixture layout: 4 complete records (54 bytes) and a
6-byte truncated tail, 60 bytes total.
"""

import verifylib

EXPECTED = [
    (1, 100, 1, "alpha"),
    (2, 65535, 128, "beta"),
    (3, 0, 0, ""),
    (7, 42, 15, "gamma-ray"),
]

EXPECTED_SUMMARY = {"records": 4, "truncated": 1, "bytes_read": 54, "bytes_total": 60}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "records.csv", ["id", "score", "flags", "name"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
