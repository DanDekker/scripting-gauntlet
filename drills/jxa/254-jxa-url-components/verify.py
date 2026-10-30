"""Grader for 254-jxa-url-components."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "urls.csv",
        ["id", "scheme", "host", "port", "path", "query_items"],
        [
            ("search", "https", "example.test", 8443, "/api/search", 2),
            ("file", "file", "", "", "/Users/dd/Library/Application Support/app/data.json", 0),
            ("health", "https", "example.test", "", "/health", 0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"urls": 3, "skipped": 1, "query_params": 2},
    )
    return failures
