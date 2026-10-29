"""Grader for 157-lua-needle-haystack.

Expected values derived from the setup script by hand: 5 text files, 1 binary file,
4 hit rows, and cross-checked against the lua and python references.
"""

import verifylib

NEEDLE = "token=100%"

EXPECTED = [
    ("alpha.log", 2, 8),
    ("crlf.log", 2, 1),
    ("sub/beta.txt", 1, 1),
    ("sub/gamma.log", 2, 3),
]

EXPECTED_SUMMARY = {"files": 5, "binary": 1, "hits": 4}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "hits.csv", ["path", "line", "column"], EXPECTED, key_count=2
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)

    # the binary file holds the needle, so a naive scan adds a row the contract forbids
    hits = io.out / "hits.csv"
    if hits.is_file() and any(
        line.split(",")[0] == "delta.bin" for line in hits.read_text(encoding="utf-8").splitlines()[1:]
    ):
        failures.append("hits.csv: delta.bin is binary and must not be scanned")
    return failures
