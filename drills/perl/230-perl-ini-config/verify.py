"""Grader for 230-perl-ini-config.

Verifies INI section parsing, inline comment stripping, and fallback to [default].
"""

import verifylib

EXPECTED = [
    ("staging", "timeout", "60", "section"),
    ("staging", "retries", "3", "default"),
    ("staging", "log_level", "debug", "section"),
    ("staging", "buffer_kb", "64", "default"),
    ("production", "retries", "5", "section"),
    ("production", "timeout", "30", "default"),
    ("production", "notify", "oncall@example.com", "section"),
    ("production", "missing_key", "MISSING", "none"),
    ("qa", "timeout", "30", "default"),
    ("default", "notify", "ops@example.com", "section"),
]

EXPECTED_SUMMARY = {"queries": 10, "section": 5, "default": 4, "missing": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "answers.csv",
        ["section", "key", "value", "source"],
        EXPECTED,
        key_count=2,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
