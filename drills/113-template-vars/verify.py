"""Grader for 113-template-vars."""

import verifylib


RENDERED = [
    "System prompt for Ada.",
    "",
    "Tone: terse. Keep every answer terse.",
    "Budget: 42 items, streaming=true, cache=null.",
    'Tags: ["fast","small"]',
    'Config: {"retries":3,"mode":"strict"}',
    "Ratio: 0.75",
    "Owner: Ada Lovelace",
    "Reviewed by [MISSING:owner]",
    "Escalate to ops@example.com or .",
    "Repeat: Ada / Ada",
    "Empty braces {{}} and a lone {{ stay literal.",
    "Split {{split_",
    "name}} stays literal too.",
    "Done.",
]


def verify(io) -> list[str]:
    failures = verifylib.lines(io.out / "rendered.txt", RENDERED)
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "placeholders": 15,
            "distinct": 12,
            "holes": 1,
            "unused": ["debug", "unused_key"],
            "defaults_used": 2,
        },
    )
    return failures
