"""Grader for 109-citation-check."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "claims.csv",
        ["number", "supported", "text"],
        [
            (1, "true", "the parser drops trailing whitespace"),
            (2, "true", "retries are  capped at three attempts"),
            (3, "true", "the loader ignores blank lines"),
            (4, "true", "The Parser Drops Trailing Whitespace"),
            (4, "false", "the retry loop never backs off"),
            (6, "false", ""),
            (8, "false", "the cache warms on first read of the config"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "claims": 7,
            "supported": 4,
            "unsupported": 3,
            "sources": 5,
            "unsupported_numbers": [4, 6, 8],
        },
    )
    return failures
