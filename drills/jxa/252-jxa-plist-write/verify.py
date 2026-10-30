"""Grader for 252-jxa-plist-write."""

import plistlib


EXPECTED = {
    "name": "agent",
    "enabled": True,
    "retry": 3,
    "note": "café",
    "labels": ["mac", "ops"],
    "limits": {"soft": 10, "hard": 20},
}


def verify(io):
    path = io.out / "report.plist"
    if not path.is_file():
        return ["missing report.plist"]
    try:
        actual = plistlib.loads(path.read_bytes())
    except Exception as exc:
        return [f"report.plist is not a valid property list: {exc}"]
    return [] if actual == EXPECTED else [f"report.plist: expected typed values, got {actual!r}"]
