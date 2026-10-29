"""Grader for 084-fd-leak."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "leaks.csv",
        ["pid", "first_fds", "last_fds", "fds_per_min", "monotonic"],
        [
            (1337, 120, 270, 30.0, "true"),
            (2011, 40, 55, 3.0, "false"),
            (902, 80, 86, 1.2, "false"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"pids": 3, "leaking": 1, "skipped": 1}
    )
    return failures
