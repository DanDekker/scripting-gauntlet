"""Grader for 184-ps1-json-depth.

Expected values derived from fixtures/config.json by hand: 7 leaves, one null, one array.
The echo check is what catches the default-depth truncation.
"""

import json

import verifylib

EXPECTED = [
    ("debug", "bool", "false"),
    ("note", "null", ""),
    ("service.limits.cpu.burst", "int", "8"),
    ("service.limits.cpu.max", "int", "4"),
    ("service.limits.mem.max_gb", "int", "16"),
    ("service.name", "string", "api"),
    ("service.tags", "array", "a|b"),
]

EXPECTED_SUMMARY = {"keys": 7, "nulls": 1, "arrays": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "flat.csv", ["key", "type", "value"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)

    echo_path = io.out / "echo.json"
    if not echo_path.is_file():
        failures.append("missing echo.json")
        return failures
    echo = json.loads(echo_path.read_text(encoding="utf-8"))
    cpu = echo.get("service", {}).get("limits", {}).get("cpu")
    if not isinstance(cpu, dict):
        failures.append(f"echo.json: service.limits.cpu was truncated to {cpu!r}")
    elif cpu.get("max") != 4 or cpu.get("burst") != 8:
        failures.append(f"echo.json: service.limits.cpu has the wrong leaves: {cpu!r}")
    if echo.get("note", "absent") is not None:
        failures.append("echo.json: note is not null")
    return failures
