"""Grader for 206-perl-exists-autoviv.

The base config has two sections (core, limits). `cache.ttl` is missing, and the
audit must not leave a `cache` section behind.
"""

import verifylib

EXPECTED_MISSING = [
    (1, "core", "host", "present"),
    (2, "core", "port", "present"),
    (3, "core", "timeout", "missing"),
    (4, "limits", "timeout", "present"),
    (5, "cache", "ttl", "missing"),
]

EXPECTED_DUMP = [
    ("core", 2),
    ("limits", 1),
]

EXPECTED_SUMMARY = {"wanted": 5, "present": 3, "missing": 2, "sections": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "missing.csv",
        ["index", "section", "key", "status"],
        EXPECTED_MISSING,
        key_count=1,
    )
    failures += verifylib.keyed_table(
        io.out / "dump.csv",
        ["section", "keys"],
        EXPECTED_DUMP,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
