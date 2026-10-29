"""Grader for 191-bash-assoc-presence.

Expected values derived from config.txt and queries.txt.
"""

import verifylib

EXPECTED = [
    ("HOST", "set", "api.internal"),
    ("DEBUG", "empty", ""),
    ("CACHE_DIR", "empty", ""),
    ("RETRIES", "missing", ""),
    ("PORT", "set", "8080"),
    ("MAX_CONNS", "missing", ""),
]

EXPECTED_SUMMARY = {"queries": 6, "set": 2, "empty": 2, "missing": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "results.csv",
        ["key", "status", "value"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
