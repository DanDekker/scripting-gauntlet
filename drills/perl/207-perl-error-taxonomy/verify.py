"""Grader for 207-perl-error-taxonomy.

exit 3 -> exit code 3 (wait status 768), exit 0 -> ok, die -> the message,
open missing -> errno 2 (ENOENT), open present -> ok with errno 0.
"""

import verifylib

EXPECTED = [
    (1, "exit", "failed", 3),
    (2, "exit", "ok", 0),
    (3, "die", "failed", "disk full"),
    (4, "open", "failed", 2),
    (5, "exit", "failed", 42),
    (6, "die", "failed", "timeout"),
    (7, "open", "ok", 0),
]

EXPECTED_SUMMARY = {"probes": 7, "failed": 5, "ok": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "results.csv",
        ["id", "kind", "status", "detail"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
