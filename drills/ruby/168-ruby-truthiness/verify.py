"""Grader for 168-ruby-truthiness.

Expected values derived from fixtures/base.json and fixtures/override.json by hand: false,
0 and "" survive, null removes the key.
"""

import verifylib

EXPECTED = [
    ("debug", "bool", "false"),
    ("extra", "int", "5"),
    ("label", "string", ""),
    ("mode", "string", "fast"),
    ("retries", "int", "0"),
]

EXPECTED_SUMMARY = {"keys": 5, "from_override": 4, "removed": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "merged.csv", ["key", "type", "value"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
