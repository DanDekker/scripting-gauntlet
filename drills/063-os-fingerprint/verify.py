"""Grader for 063-os-fingerprint."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "hosts.csv",
        ["platform", "hostname", "name", "version", "architecture"],
        [
            ("linux", "app-01", "Ubuntu", "24.04", "x86_64"),
            ("macos", "mbp-02", "macOS", "15.1", "arm64"),
            ("windows", "OPS-07", "Windows 11 Pro", "23H2", "x86_64"),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"platforms": 3})
    return failures
