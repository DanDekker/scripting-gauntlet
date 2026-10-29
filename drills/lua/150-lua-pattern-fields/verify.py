"""Grader for 150-lua-pattern-fields.

Expected values derived from fixtures/report.txt by hand (8 distinct keys, 1 duplicate,
2 invalid lines) and cross-checked against the bash and lua references.
"""

import verifylib

EXPECTED = [
    ("blank", ""),
    ("name", "final report"),
    ("note", "costs $5,000 and 100% of budget"),
    ("owner", "Ada Lovelace"),
    ("path", "/var/log/app.log"),
    ("quoted", "a=b"),
    ("tag", "a=b"),
    ("window", "2026-10-01..2026-10-29"),
]

EXPECTED_SUMMARY = {"keys": 8, "duplicates": 1, "invalid": 2}


def verify(io):
    failures = verifylib.keyed_table(
        io.out / "fields.csv", ["key", "value"], EXPECTED, key_count=1
    )
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
