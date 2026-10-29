"""Grader for 116-tool-args."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "errors.csv",
        ["call_id", "error"],
        [
            ("c4", "missing:path"),
            ("c5", "unknown:colour"),
            ("c6", "type:path"),
            ("c7", "type:limit"),
            ("c8", "min:limit"),
            ("c9", "enum:mode"),
            ("c11", "type:path"),
            ("c12", "type:limit"),
            ("c18", "missing:path"),
            ("c20", "type:path"),
            ("c20", "enum:mode"),
            ("c21", "missing:path"),
            ("c21", "unknown:extra"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "calls": 21,
            "valid": 10,
            "invalid": 11,
            "errors": 13,
            "wrong_tool": 2,
            "bad_arguments": 2,
        },
    )
    return failures
