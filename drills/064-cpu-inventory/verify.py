"""Grader for 064-cpu-inventory."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "cpus.csv",
        ["platform", "processor", "physical_cores", "logical_cpus", "threads_per_core", "architecture"],
        [
            ("linux", "AMD EPYC 7313P 16-Core Processor", 4, 8, 2, "x86_64"),
            ("macos", "Apple M3 Pro", 11, 11, 1, "arm64"),
            ("windows", "AMD EPYC 9374F 32-Core Processor", 8, 16, 2, "x86_64"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"hosts": 3, "physical_cores": 23, "logical_cpus": 35}
    )
    return failures
