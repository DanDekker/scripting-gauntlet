"""Grader for 129-crawl-frontier."""

import verifylib

ROWS = [
    ("http://example.com/", 0, 3),
    ("http://example.com/a", 1, 4),
    ("http://example.com/b", 1, 2),
    ("http://example.com/dir", 1, 2),
    ("http://example.com/deep/c", 2, 2),
    ("http://example.com/dir/", 2, 2),
    ("http://example.com/deep/e", 2, 2),
    ("http://example.com/x?q=1", 2, 1),
    ("http://example.com/deep/f", 3, 1),
]

SUMMARY = {
    "visited": 9,
    "skipped": 10,
    "limit_reached": True,
    "max_depth_reached": 3,
    "orphan": 3,
}


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "pages.csv", ["url", "depth", "inbound"], ROWS)
    failures += verifylib.json_eq(io.out / "summary.json", SUMMARY)
    return failures
