"""Grader for 160-lua-file-hunt.

Expected values derived from the setup script by hand: 6 files scanned, 2 matched,
240 bytes, and cross-checked against the lua and python references.
"""

import verifylib

EXPECTED = [
    ("a.log", 140),
    ("sub/d.log", 100),
]

EXPECTED_SUMMARY = {"matched": 2, "bytes": 240, "scanned": 6}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "found.csv", ["path", "size"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
