"""Grader for 114-md-links."""

import verifylib


LINKS = [
    ("README.md", 3, "#overview", "ok"),
    ("README.md", 3, "sub/other.md", "ok"),
    ("README.md", 5, "guide/advanced.md#getting-started", "ok"),
    ("README.md", 7, "missing.md", "broken"),
    ("README.md", 9, "#Overview", "missing-anchor"),
    ("README.md", 11, "sub/other.md#setup", "ok"),
    ("README.md", 11, "sub/other.md#deep-dive", "ok"),
    ("README.md", 13, "sub/nested/notes.md#scratch-notes", "ok"),
    ("README.md", 15, "my%20file.md", "ok"),
    ("README.md", 15, "meta.txt", "ok"),
    ("README.md", 17, "sub/", "ok"),
    ("README.md", 17, "nowhere/", "broken"),
    ("README.md", 19, "", "empty"),
    ("guide/advanced.md", 3, "../README.md", "ok"),
    ("guide/advanced.md", 3, "../sub/other.md#setup", "ok"),
    ("guide/advanced.md", 5, "../sub/other.md#Setup", "missing-anchor"),
    ("guide/advanced.md", 7, "../sub/other.md#setup", "ok"),
    ("guide/advanced.md", 9, "../sub/nested/notes.md", "ok"),
    ("guide/advanced.md", 9, "../sub/nested/notes.md#first-pass", "ok"),
    ("guide/advanced.md", 11, "../my%20file.md#title-here", "ok"),
    ("sub/nested/notes.md", 3, "../../README.md", "ok"),
    ("sub/nested/notes.md", 3, "../../sub/other.md#deep-dive", "ok"),
    ("sub/nested/notes.md", 5, "#no-such-heading", "missing-anchor"),
    ("sub/nested/notes.md", 5, "#scratch-notes", "ok"),
    ("sub/nested/notes.md", 7, "./deep.md", "broken"),
    ("sub/other.md", 9, "nested/notes.md#scratch-notes", "ok"),
    ("sub/other.md", 9, "../README.md#overview", "ok"),
]


def verify(io) -> list[str]:
    failures = verifylib.table(io.out / "links.csv", ["file", "line", "target", "status"], LINKS)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files": 5,
            "links": 27,
            "ok": 20,
            "broken": 3,
            "missing_anchor": 3,
            "empty": 1,
            "external": 2,
        },
    )
    return failures
