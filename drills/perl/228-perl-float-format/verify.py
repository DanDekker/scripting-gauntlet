"""Grader for 228-perl-float-format.

plain: perl's default 15-significant-digit printing (3.0 -> "3").
cents: %.2f of the double (2.675 -> "2.67", 0.125 -> "0.12").
whole: %.0f, midpoint to even (2.5 -> "2", 3.5 -> "4", 0.5 -> "0").
"""

import verifylib

EXPECTED = [
    ("alpha", "2.675", "2.67", "3"),
    ("bravo", "0.125", "0.12", "0"),
    ("charlie", "1.005", "1.00", "1"),
    ("delta", "3", "3.00", "3"),
    ("echo", "-2.5", "-2.50", "-2"),
    ("foxtrot", "3.5", "3.50", "4"),
    ("golf", "2.5", "2.50", "2"),
    ("hotel", "1.25", "1.25", "1"),
    ("india", "0.5", "0.50", "0"),
    ("juliet", "10", "10.00", "10"),
    ("kilo", "0.145", "0.14", "0"),
    ("lima", "4.5", "4.50", "4"),
    ("mike", "-4.5", "-4.50", "-4"),
    ("nina", "0.123456789012346", "0.12", "0"),
    ("oscar", "3.9", "3.90", "4"),
    ("peggy", "-3.9", "-3.90", "-4"),
]

EXPECTED_SUMMARY = {"amounts": 16, "total_cents": "22.32", "max_plain": "10"}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "amounts.csv",
        ["label", "plain", "cents", "whole"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
