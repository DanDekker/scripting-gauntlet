"""Grader for 203-perl-slurp-record-separator.

notes.txt holds three records: two lines, one line, two lines.
config.ini holds six lines and five key=value settings.
"""

import verifylib

EXPECTED = [
    (1, "First note line", 2),
    (2, "Second note only", 1),
    (3, "Third note", 2),
]

EXPECTED_SUMMARY = {
    "records": 3,
    "total_lines": 5,
    "config_lines": 6,
    "settings": 5,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "records.csv",
        ["index", "title", "lines"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
