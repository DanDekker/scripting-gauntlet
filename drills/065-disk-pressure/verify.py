"""Grader for 065-disk-pressure."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "low_space.csv",
        ["platform", "volume", "total_bytes", "free_bytes", "free_pct"],
        [
            ("macos", "/", 102400000000, 8192000000, 8.0),
            ("windows", "C:\\ (OS)", 107374182400, 8589934592, 8.0),
            ("linux", "/", 10240000000, 1024000000, 10.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"volumes_seen": 7, "low_space": 3}
    )
    return failures
