"""Grader for 097-doc-chunker."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "chunks.csv",
        ["id", "doc", "section", "tokens", "chars"],
        [
            ("faq.md#(preamble)#1", "faq.md", "(preamble)", 5, 30),
            ("faq.md#Common questions#2", "faq.md", "Common questions", 6, 25),
            ("faq.md#Common questions#3", "faq.md", "Common questions", 7, 48),
            ("faq.md#Another section#5", "faq.md", "Another section", 5, 30),
            ("guide.md#Setup#1", "guide.md", "Setup", 9, 49),
            ("guide.md#Setup#3", "guide.md", "Setup", 2, 8),
            ("guide.md#Setup#4", "guide.md", "Setup", 6, 28),
            ("guide.md#Setup#5", "guide.md", "Setup", 52, 316),
            ("guide.md#Troubleshooting#6", "guide.md", "Troubleshooting", 6, 26),
            ("release-notes.md#(preamble)#1", "release-notes.md", "(preamble)", 4, 19),
            ("release-notes.md#(preamble)#3", "release-notes.md", "(preamble)", 6, 33),
            ("release-notes.md#(preamble)#4", "release-notes.md", "(preamble)", 5, 29),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "documents": 4,
            "total_chunks": 12,
            "duplicates_dropped": 7,
            "empty_dropped": 2,
            "tokens": 113,
        },
    )
    return failures
