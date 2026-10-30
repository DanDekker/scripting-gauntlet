"""Grader for 213-perl-truthy-zero.

Perl truth: only "" and "0" are false. So feature_b and feature_g are off;
feature_c (0.0), feature_d (00), feature_e (false) and feature_f (no) are on.
"""

import verifylib

EXPECTED = [
    (1, "feature_a", "1", "on"),
    (2, "feature_b", "0", "off"),
    (3, "feature_c", "0.0", "on"),
    (4, "feature_d", "00", "on"),
    (5, "feature_e", "false", "on"),
    (6, "feature_f", "no", "on"),
    (7, "feature_g", "", "off"),
]

EXPECTED_SUMMARY = {"settings": 7, "on": 5, "off": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "settings.csv",
        ["index", "name", "value", "state"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
