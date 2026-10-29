"""Grader for 092-prompt-diff."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "changes.csv",
        ["change", "line"],
        [
            ("removed", "Never delete files outside the workspace."),
            ("removed", "Session log path: /var/log/scriptbot.log"),
            ("added", "Prefer small, reviewable diffs."),
            ("added", "If a tool call fails twice, stop and report the error."),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"removed": 2, "added": 2, "unchanged": 6, "guardrails_removed": 1},
    )
    return failures
