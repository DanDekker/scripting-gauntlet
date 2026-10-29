"""Grader for 167-ruby-hash-identity.

Expected values derived from fixtures/events.jsonl by hand: 1/1.0 merge (4 events), "1"
is its own row (2 events), 2 and "2" are one event each, two invalid entries.
"""

import verifylib

EXPECTED = [
    ("1", "numeric", 4),
    ("1", "string", 2),
    ("2", "numeric", 1),
    ("2", "string", 1),
]

EXPECTED_SUMMARY = {"ids": 4, "events": 8, "invalid": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "tally.csv", ["id", "kind", "events"], EXPECTED, key_count=2
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
