"""Grader for 151-lua-exact-decimals.

Expected values derived from fixtures/measurements.csv by hand and cross-checked
against the lua and python references.
"""

import verifylib

EXPECTED = [
    ("alpha", 3, "-0.250", "42.500", "84.250"),
    ("beta", 2, "-3.000", "7.000", "4.000"),
    ("gamma", 1, "0.125", "0.125", "0.125"),
]

EXPECTED_SUMMARY = {"sensors": 3, "records": 6, "invalid": 1, "total": "88.375"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "sensors.csv",
        ["sensor", "count", "min", "max", "total"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
