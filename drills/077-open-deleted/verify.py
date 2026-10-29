"""Grader for 077-open-deleted."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "deleted.csv",
        ["pid", "command", "bytes_mb", "files"],
        [
            (1337, "python3", 4096.0, 2),
            (412, "nginx", 2048.0, 1),
            (902, "postgres", 512.0, 1),
            (2011, "redis", 100.0, 1),
            (1, "systemd", 8.0, 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"processes": 5, "files": 6, "reclaimable_mb": 6764.0, "top_pid": 1337},
    )
    return failures
