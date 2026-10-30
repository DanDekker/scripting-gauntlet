"""Grader for 240-ps1-split-regex.

A regex split on '|' or '.' mangles the fields; the fixtures cover both metacharacters
plus one genuinely malformed row (a two-part version).
"""

import verifylib

EXPECTED = [
    ("web", 1, 10, 2, "a3f9c1d", 20480),
    ("api", 2, 0, 11, "9be7f02", 40960),
    ("web", 1, 9, 14, "c0ffee1", 1024),
    ("cli", 0, 4, 0, "deadb3e", 512),
]

EXPECTED_SUMMARY = {
    "rows": 4,
    "malformed": 1,
    "total_size": 62976,
    "packages": 3,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "builds.csv",
        ["pkg", "major", "minor", "patch", "sha", "size"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
