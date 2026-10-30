"""Grader for 205-perl-foreach-alias.

The original list must survive normalization: `ada lovelace` stays lowercase in
out/original.csv, and the trimmed `  grace hopper` is reported as read.
"""

import verifylib

EXPECTED_NORMALIZED = [
    (1, "Ada lovelace"),
    (2, "Grace hopper"),
    (3, "ALAN TURING"),
    (4, "Jean-luc picard"),
]

EXPECTED_ORIGINAL = [
    (1, "ada lovelace"),
    (2, "grace hopper"),
    (3, "ALAN TURING"),
    (4, "jean-luc picard"),
]

EXPECTED_SUMMARY = {"names": 4, "changed": 3}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "normalized.csv",
        ["index", "name"],
        EXPECTED_NORMALIZED,
        key_count=1,
    )
    failures += verifylib.keyed_table(
        io.out / "original.csv",
        ["index", "name"],
        EXPECTED_ORIGINAL,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
