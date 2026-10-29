"""Grader for 180-perl-substitution-eval.

Expected values derived by hand: three pairs, one pair, two pairs, one empty-valued pair.
"""

import verifylib

EXPECTED = [
    (1, "A:1 B:2 C:3", 3),
    (2, "X:10", 1),
    (3, "NAME:ALICE ROLE:ADMIN", 2),
    (4, "EMPTY:", 1),
]

EXPECTED_SUMMARY = {"lines": 4, "substitutions": 7}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "rewritten.csv", ["line", "text", "substitutions"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
