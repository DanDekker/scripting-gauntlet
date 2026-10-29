"""Grader for 070-env-merge."""

import verifylib


EXPECTED = {
    "APP_NAME": "deck",
    "DB_URL": "postgres://localhost/deck",
    "DEBUG_FLAG": "",
    "EMPTY": "now set",
    "GREETING": "hello",
    "LOG_LEVEL": "debug",
    "PORT": "9000",
    "SINGLE": "single # not a comment",
}


def verify(io):
    failures = verifylib.json_eq(io.out / "config.json", EXPECTED)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files": 2, "keys": 8, "overridden": 3, "empty": 1},
    )
    return failures
