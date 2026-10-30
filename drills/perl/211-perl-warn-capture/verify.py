"""Grader for 211-perl-warn-capture.

Three warnings are watched and captured without the location suffix; the final
warning is emitted after the handler is gone and must not be captured.
"""

import verifylib

EXPECTED = [
    (1, "disk nearly full"),
    (2, "cache miss for alpha"),
    (3, "rotation started"),
]

EXPECTED_SUMMARY = {"emitted": 4, "captured": 3, "final_captured": "false"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "warnings.csv",
        ["index", "message"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
