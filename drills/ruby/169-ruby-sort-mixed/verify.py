"""Grader for 169-ruby-sort-mixed.

Expected values derived from fixtures/records.jsonl by hand: ties at 10 keep input order
(g, a, d), "9" loses to 10, missing scores rank last.
"""

import verifylib

EXPECTED = [
    (1, "g", 10),
    (2, "a", 10),
    (3, "d", 10),
    (4, "b", 9),
    (5, "c", ""),
    (6, "f", ""),
]

EXPECTED_SUMMARY = {"lines": 7, "ranked": 6, "invalid": 1, "missing": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "ranked.csv", ["rank", "name", "score"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
