"""Grader for 158-lua-plugin-order.

Expected values derived from fixtures/plugins.txt by hand: 10 distinct plugins, 5
loadable, 5 failed, and cross-checked against the lua and python references.
"""

import verifylib

EXPECTED_ORDER = [
    (1, "log"),
    (2, "store"),
    (3, "auth"),
    (4, "http"),
    (5, "cache"),
]

EXPECTED_ERRORS = [
    ("mail", "missing-dep:smtp"),
    ("metrics", "duplicate-name"),
    ("report", "blocked:mail"),
    ("sync", "cycle"),
    ("sync2", "cycle"),
]

EXPECTED_SUMMARY = {"plugins": 10, "loaded": 5, "failed": 5}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "order.csv", ["position", "name"], EXPECTED_ORDER, key_count=1
    )
    failures += verifylib.keyed_table(
        io.out / "errors.csv", ["name", "reason"], EXPECTED_ERRORS, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
