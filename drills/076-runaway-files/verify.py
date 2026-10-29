"""Grader for 076-runaway-files."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "top_files.csv",
        ["rank", "path", "size_mb"],
        [
            (1, "home/pp/backups/dump.sql", 10.0),
            (2, "var/log/app.log.1", 8.0),
            (3, "var/cache/blob.bin", 5.0),
            (4, "var/log/app.log", 3.0),
            (5, "var/log/old/app-2025.log", 1.5),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files": 7, "bytes": 29537040, "ignored_bytes": 6291456, "links_skipped": 1},
    )
    return failures
