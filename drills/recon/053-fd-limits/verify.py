"""Grader for 053-fd-limits.

Counted by hand from fixtures/fd-listing.txt: 68 descriptor rows over 5 pids —
2088=20, 4127=18, 3310=16, 1012=9, 3140=5 — against a soft limit of 16, so three
processes are flagged (3310 sits exactly on the limit).
"""

import verifylib

COUNTS = [
    (2088, 20),
    (4127, 18),
    (3310, 16),
    (1012, 9),
    (3140, 5),
]

FLAGGED = [
    (2088, 20, 16),
    (3310, 16, 16),
    (4127, 18, 16),
]

SUMMARY = {"processes": 5, "descriptors": 68, "limit": 16, "flagged": 3}


def verify(io):
    failures = verifylib.table(io.out / "fd-counts.csv", ["pid", "descriptors"], COUNTS)
    failures += verifylib.table(io.out / "flagged.csv", ["pid", "descriptors", "limit"], FLAGGED)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
