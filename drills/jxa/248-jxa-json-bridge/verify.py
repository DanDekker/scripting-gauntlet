"""Grader for 248-jxa-json-bridge."""

import verifylib


EXPECTED = {
    "records": [
        {"id": "a", "owner_state": "null", "owner": "", "tags": ["mac", "prod"], "enabled": True},
        {"id": "b", "owner_state": "value", "owner": "Lee", "tags": [], "enabled": False},
        {"id": "c", "owner_state": "missing", "owner": "", "tags": ["mac"], "enabled": True},
    ],
    "summary": {"records": 3, "null_owner": 1, "missing_owner": 1, "tagged": 2},
}


def verify(io):
    return verifylib.json_eq(io.out / "report.json", EXPECTED)
