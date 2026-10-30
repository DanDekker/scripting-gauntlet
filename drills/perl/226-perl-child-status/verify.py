"""Grader for 226-perl-child-status.

system() returns the raw wait status (exit 3 -> 768). The exit code is $? >> 8 and
the signal is $? & 127, so a signalled child has exit code 0. A program that cannot
be executed makes system() return -1 and $? -1.
"""

import verifylib

EXPECTED = [
    (1, "exit", "ok", 0),
    (2, "exit", "failed", 3),
    (3, "exit", "failed", 42),
    (4, "signal", "signalled", 9),
    (5, "signal", "signalled", 15),
    (6, "missing", "notfound", -1),
]

EXPECTED_SUMMARY = {"probes": 6, "ok": 1, "failed": 2, "signalled": 2, "notfound": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "results.csv",
        ["id", "kind", "status", "detail"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
