"""Grader for 156-lua-sparse-array.

Expected values derived from fixtures/values.txt by hand: 8 positions, 5 present,
3 missing (two empty lines plus the invalid one), 1 invalid, total 100, max 40, and
cross-checked against the lua and python references.
"""

import verifylib

EXPECTED = [
    (1, 10),
    (2, 20),
    (4, 40),
    (6, 0),
    (7, 30),
]

EXPECTED_SUMMARY = {
    "positions": 8,
    "present": 5,
    "missing": 3,
    "invalid": 1,
    "total": 100,
    "max": 40,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "present.csv", ["position", "value"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
