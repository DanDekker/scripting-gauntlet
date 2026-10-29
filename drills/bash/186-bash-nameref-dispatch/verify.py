"""Grader for 186-bash-nameref-dispatch.

Expected values derived by hand from fixtures/actions.txt:
alpha cpu: 15, alpha mem: 4
beta io: 3, beta mem: 20
gamma disk: 150
Total: 192 across 5 metric entries in 3 categories.
"""

import verifylib

EXPECTED = [
    ("alpha", "cpu", 15),
    ("alpha", "mem", 4),
    ("beta", "io", 3),
    ("beta", "mem", 20),
    ("gamma", "disk", 150),
]

EXPECTED_SUMMARY = {"categories": 3, "entries": 5, "total": 192}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "tallies.csv",
        ["category", "metric", "total"],
        EXPECTED,
        key_count=2,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
