"""Grader for 183-ruby-encoding-scrub.

Expected values derived from the fixture bytes: cafe is 4 chars / 5 bytes, the broken line
is 4 chars / 4 bytes after scrub.
"""

import verifylib

EXPECTED = [
    (1, "true", 4, 5, "café"),
    (2, "false", 4, 4, "caf?"),
    (3, "true", 2, 2, "ok"),
]

EXPECTED_SUMMARY = {"lines": 3, "invalid": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "lines.csv", ["line", "valid", "chars", "bytes", "text"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
