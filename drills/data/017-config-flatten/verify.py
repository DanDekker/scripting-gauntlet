"""Grader for 017-config-flatten."""

import verifylib

EXPECTED = {
    "name": "scriptdeck",
    "version": 3,
    "features.0": "api",
    "features.1": "scrape",
    "limits.timeout": 30,
    "limits.retries": 2,
}


def verify(io):
    failures = verifylib.json_eq(io.out / "flat.json", EXPECTED)
    failures += verifylib.json_eq(io.out / "summary.json", {"keys": len(EXPECTED)})
    return failures
