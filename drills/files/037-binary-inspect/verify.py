"""Grader for 037-binary-inspect.

Offsets and counts are the contract in PROMPT.md applied by hand to setup.py's blob:
6 strings, 20 NULs, the PNG signature at offset 23, 111 bytes total.
"""

import verifylib

STRINGS = [
    "3\tscriptdeck blob v1",
    "35\tIHDR",
    "43\tchunk-meta",
    "58\tvendor: acme corp",
    "80\tbuild",
    "86\tdate=2026-10-29",
]


def verify(io):
    failures = verifylib.lines(io.out / "strings.txt", STRINGS)
    failures += verifylib.json_eq(
        io.out / "report.json",
        {
            "size_bytes": 111,
            "nul_bytes": 20,
            "string_count": 6,
            "embedded_magic": "png",
            "magic_offset": 23,
        },
    )
    return failures
