"""Grader for 161-perl-split-limits.

Expected values derived from fixtures/rows.txt by hand: 3 accepted, 4 rejected, and
cross-checked against the perl and python references.
"""

import verifylib

EXPECTED = [
    ("alice", "admin", "", "7"),
    ("bob", "user", "ok", ""),
    ("carol", "admin", "ok", "10"),
]

EXPECTED_SUMMARY = {"rows": 3, "empty_notes": 1, "empty_scores": 1, "invalid": 4}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "rows.csv", ["name", "role", "note", "score"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
