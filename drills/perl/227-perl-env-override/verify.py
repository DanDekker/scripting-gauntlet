"""Grader for 227-perl-env-override.

local $ENV{NAME} scopes the override to the block, so a later child sees the variable
as absent and the parent environment is back to its starting state. An empty value is
still a value.
"""

import verifylib

EXPECTED = [
    (1, "DRILL_ONE", "alpha", "DRILL_ONE", "=alpha", "unset"),
    (2, "DRILL_TWO", "beta", "DRILL_ONE", "unset", "unset"),
    (3, "DRILL_ONE", "gamma", "DRILL_TWO", "unset", "unset"),
    (4, "DRILL_THREE", "", "DRILL_THREE", "=", "unset"),
]

EXPECTED_SUMMARY = {"steps": 4, "seen_set": 2, "leaked": 0}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "steps.csv",
        ["id", "set_var", "value", "watch_var", "seen", "after"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
