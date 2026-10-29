"""Grader for 178-lua-number-printing.

Expected values derived from the Lua 5.5 probe: tostring keeps the float subtype and uses
shortest round-trip, %.17g exposes the double, and 1e15/1e16 render scientifically.
"""

import verifylib

EXPECTED = [
    ("1", "integer", "1", "1", "1"),
    ("1.0", "float", "1.0", "1", "1"),
    ("0.1", "float", "0.1", "0.10000000000000001", "0.1"),
    ("1e15", "float", "1e+15", "1000000000000000", "1e+15"),
    ("1000000000000000", "integer", "1000000000000000", "1000000000000000", "1e+15"),
    ("2.5", "float", "2.5", "2.5", "2.5"),
    ("1e16", "float", "1e+16", "10000000000000000", "1e+16"),
    ("9007199254740993", "integer", "9007199254740993", "9007199254740992", "9.0072e+15"),
    ("0.5", "float", "0.5", "0.5", "0.5"),
    ("abc", "invalid", "", "", ""),
]

EXPECTED_SUMMARY = {
    "rows": 10,
    "integers": 3,
    "floats": 6,
    "invalid": 1,
    "scientific": 2,
}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "numbers.csv",
        ["token", "kind", "plain", "full", "short"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
