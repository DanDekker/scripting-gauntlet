"""Grader for 262-tcl-list-quoting."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "commands.csv",
        ["command", "target", "args"],
        [("deploy", "web app", 3), ("backup", "/tmp/My File", 2), ("rotate", "logs", 3)],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"commands": 3, "with_spaces": 2})
    return failures
