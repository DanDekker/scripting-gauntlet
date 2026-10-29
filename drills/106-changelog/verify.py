"""Grader for 106-changelog."""

import verifylib

EXPECTED = """## Features
- add csv support
- new layout
- add flag
- support windows paths

## Bug Fixes
- handle empty input
- repair tooltip

## Performance
- memoise lookups

## Refactoring
- drop legacy api

## Documentation
- update readme

## Breaking Changes
- drop legacy api
- new layout
- memoise lookups
- switch to esbuild
"""


def verify(io) -> list[str]:
    failures = verifylib.lines(io.out / "changelog.md", EXPECTED.splitlines())
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "commits": 15,
            "conventional": 13,
            "skipped": 2,
            "internal": 4,
            "breaking": 4,
            "features": 4,
            "fixes": 2,
        },
    )
    return failures
