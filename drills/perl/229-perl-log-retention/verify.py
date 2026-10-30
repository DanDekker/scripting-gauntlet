"""Grader for 229-perl-log-retention.

Verifies retention policy actions and age calculation.
access-2026-10-28.log (age 2) -> keep
access-2026-10-25.log (age 5) -> compress
access-2026-10-20.log.gz (age 10, already .gz) -> keep
access-2026-10-10.log (age 20) -> delete
access-2026-10-05.log.gz (age 25) -> delete
error-2026-10-27.log (age 3) -> compress
worker-temp.tmp (.tmp) -> delete (age empty)
README.txt (other) -> ignore (age empty)
"""

import verifylib

EXPECTED = [
    ("README.txt", "", "ignore"),
    ("access-2026-10-05.log.gz", 25, "delete"),
    ("access-2026-10-10.log", 20, "delete"),
    ("access-2026-10-20.log.gz", 10, "keep"),
    ("access-2026-10-25.log", 5, "compress"),
    ("access-2026-10-28.log", 2, "keep"),
    ("error-2026-10-27.log", 3, "compress"),
    ("worker-temp.tmp", "", "delete"),
]

EXPECTED_SUMMARY = {"files": 8, "keep": 2, "compress": 2, "delete": 3, "ignore": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "retention.csv",
        ["file", "age_days", "action"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
