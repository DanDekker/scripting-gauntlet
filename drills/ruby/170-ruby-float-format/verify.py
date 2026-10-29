"""Grader for 170-ruby-float-format.

Expected values derived from the probe: format("%.2f", 1.005) is "1.00" while round(2)
gives 1.01, so the contract asks for rounding on the decimal value.
"""

import verifylib

EXPECTED = [
    ("12", "int", "12"),
    ("3.0", "float", "3.00"),
    ("1e20", "float", "100000000000000000000.00"),
    ("2.675", "float", "2.68"),
    ("1.005", "float", "1.01"),
    ("-0.5", "float", "-0.50"),
    ("0", "int", "0"),
    ("abc", "invalid", ""),
]

EXPECTED_SUMMARY = {"lines": 8, "int": 2, "float": 5, "invalid": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "formatted.csv", ["raw", "kind", "formatted"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
