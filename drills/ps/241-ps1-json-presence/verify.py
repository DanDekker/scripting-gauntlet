"""Grader for 241-ps1-json-presence."""

import verifylib


EXPECTED_ROWS = [
    ("alpha", "null", "", "zero", 0),
    ("beta", "missing", "", "positive", 5),
    ("gamma", "empty", "", "null", ""),
    ("delta", "value", "Ada", "positive", 12),
    ("epsilon", "value", "0", "negative", -2),
]

EXPECTED_SUMMARY = {
    "records": 5,
    "owner_missing": 1,
    "owner_null": 1,
    "owner_empty": 1,
    "quota_missing": 0,
    "quota_null": 1,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "report.csv",
        ["id", "owner_state", "owner_value", "quota_state", "quota_value"],
        EXPECTED_ROWS,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
