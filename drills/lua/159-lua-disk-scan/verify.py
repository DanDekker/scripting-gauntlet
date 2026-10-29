"""Grader for 159-lua-disk-scan.

Expected values derived from the setup script by hand: 8 files, 412 bytes, 2 skipped
directories, and cross-checked against the lua and python references.
"""

import verifylib

EXPECTED = [
    ("log", 3, 350),
    ("gz", 1, 40),
    ("txt", 1, 10),
    ("md", 1, 7),
    ("", 2, 5),
]

EXPECTED_SUMMARY = {"files": 8, "bytes": 412, "dirs_skipped": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "bytes.csv", ["ext", "count", "bytes"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
