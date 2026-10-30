"""Grader for 208-perl-crlf-strip.

Both readings are valid: a CRLF file read with chomp alone leaves "\\r" on the
value, which fails the anchored pattern.
"""

import verifylib

EXPECTED = [
    ("s1", "room a", "21.5", "ok"),
    ("s2", "room b", "19.0", "ok"),
]

EXPECTED_SUMMARY = {"readings": 2, "valid": 2, "malformed": 0}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "readings.csv",
        ["sensor", "label", "value", "status"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
