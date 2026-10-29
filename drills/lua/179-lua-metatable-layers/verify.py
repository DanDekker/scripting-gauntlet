"""Grader for 179-lua-metatable-layers.

Expected values derived from the layer fixture: leaf inherits mid inherits base, so
provenance has to be walked, not guessed.
"""

import verifylib

EXPECTED = [
    ("leaf", "retries", "5", "mid", "false"),
    ("leaf", "region", "eu", "base", "false"),
    ("leaf", "tier", "gold", "mid", "false"),
    ("leaf", "name", "api", "leaf", "true"),
    ("leaf", "missing", "", "absent", "false"),
    ("mid", "retries", "5", "mid", "true"),
    ("base", "region", "eu", "base", "true"),
    ("base", "tier", "", "absent", "false"),
]

EXPECTED_KEYS = [
    ("base", "region;retries"),
    ("leaf", "name"),
    ("mid", "retries;tier"),
]

EXPECTED_SUMMARY = {"layers": 3, "lookups": 8, "resolved": 6, "absent": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "lookups.csv", ["layer", "key", "value", "source", "own"], EXPECTED, key_count=2
    )
    failures += verifylib.keyed_table(
        io.out / "own_keys.csv", ["layer", "keys"], EXPECTED_KEYS, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
