"""Grader for 152-lua-utf8-chars.

Expected values derived from the setup script by hand: 7 lines, one of them invalid
(raw 0xFF), and cross-checked against the lua and python references.
"""

import verifylib

EXPECTED = [
    (1, 11, 11, "hello worl"),
    (2, 4, 5, "café"),
    (3, 3, 9, "日本語"),
    (4, 5, 6, "naïve"),
    (6, 10, 13, "emoji 🎉 ok"),
    (7, 18, 18, "truncate m"),
]

EXPECTED_SUMMARY = {"lines": 7, "valid": 6, "invalid": 1, "chars": 51, "bytes": 62}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "chars.csv", ["line", "chars", "bytes", "head"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
