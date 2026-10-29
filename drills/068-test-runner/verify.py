"""Grader for 068-test-runner."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "results.csv",
        ["test", "exit_code", "stdout", "stderr"],
        [
            ("unit", 0, "PASS unit", ""),
            ("schema", 0, "PASS schema", ""),
            ("config", 0, "PASS config", ""),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"tests": 3, "passed": 3, "failed": 0})
    state = io.work / "ran"
    for name in ("unit", "schema", "config"):
        if not (state / name).is_file():
            failures.append(f"test case was not executed: {name}")
    return failures
