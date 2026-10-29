"""Grader for 162-perl-numify.

Expected values derived from fixtures/values.txt by hand and cross-checked against the
perl and python references.
"""

import verifylib

EXPECTED = [
    ("42", "int", "42"),
    ("-3.7", "decimal", "-3"),
    ("010", "int", "10"),
    ("0x10", "invalid", ""),
    ("1e3", "invalid", ""),
    ("abc", "invalid", ""),
    ("42", "int", "42"),
    ("-0.5", "decimal", "0"),
    ("3.999", "decimal", "3"),
    ("+7", "int", "7"),
    (".5", "decimal", "0"),
]

EXPECTED_SUMMARY = {"rows": 11, "int": 4, "decimal": 4, "invalid": 3}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "values.csv", ["token", "kind", "int_part"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
