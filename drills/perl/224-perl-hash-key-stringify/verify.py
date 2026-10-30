"""Grader for 224-perl-hash-key-stringify.

Lookups are matched as text: 8080 hits "gadgets", 8079 misses, 007 hits "bolts",
1.0 hits "small". A numeric coercion misses 007 and 1.0.
"""

import verifylib

EXPECTED = [
    (1, "8080", "hit", "gadgets"),
    (2, "8079", "miss", ""),
    (3, "007", "hit", "bolts"),
    (4, "1.0", "hit", "small"),
]

EXPECTED_SUMMARY = {"lookups": 4, "hits": 3, "misses": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "lookups.csv",
        ["index", "lookup", "status", "name"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
