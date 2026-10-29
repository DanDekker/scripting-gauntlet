"""Grader for 171-lua-integer-subtype.

Expected values derived from the Lua 5.5 probe: // and % floor and keep the subtype,
math.fmod truncates, and maxinteger + 1 wraps.
"""

import verifylib

EXPECTED = [
    ("10", "integer", "1", "3", "3"),
    ("-10", "integer", "-2", "4", "-3"),
    ("7", "integer", "1", "0", "0"),
    ("-7", "integer", "-1", "0", "0"),
    ("0", "integer", "0", "0", "0"),
    ("3.5", "float", "0.0", "3.5", "3.5"),
    ("-0.5", "float", "-1.0", "6.5", "-0.5"),
    ("0x10", "integer", "2", "2", "2"),
    ("-0x10", "integer", "-3", "5", "-2"),
    ("abc", "invalid", "", "", ""),
]

COUNTERS = [("-9223372036854775808", "8000000000000000", "true")]

EXPECTED_SUMMARY = {"rows": 10, "integers": 7, "floats": 2, "invalid": 1}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "values.csv",
        ["token", "kind", "quotient", "remainder", "fmod"],
        EXPECTED,
        key_count=1,
    )
    failures += verifylib.keyed_table(
        io.out / "counters.csv", ["total", "total_hex", "wrapped"], COUNTERS, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
