"""Grader for 120-junit-report."""

import csv
import re

import verifylib

THREE_DECIMALS = re.compile(r"^\d+\.\d{3}$")


def verify(io) -> list[str]:
    tests = io.out / "tests.csv"
    failures = verifylib.table(
        tests,
        ["suite", "class", "name", "status", "time"],
        [
            ("suite.a", "pkg.mod", "test_one", "pass", 0.100),
            ("suite.a", "pkg.mod", "test_two", "fail", 0.200),
            ("suite.a", "pkg.mod", "test_three", "skip", 0.300),
            ("suite.b", "pkg.mod.sub", "test_four", "pass", 1.250),
            ("suite.b", "", "test_five handles empty file", "fail", 0.000),
            ("", "pkg.loose", "test_six", "fail", 0.000),
            ("suite.c", "pkg.mod", "test_seven", "error", 1.250),
            ("suite.c", "pkg.mod", "test_config & env", "pass", 0.500),
            ("suite.c", "pkg.mod", "test_nine", "pass", 0.500),
            ("suite.d", "", "test_ten", "error", 0.005),
        ],
    )

    if tests.is_file():
        with tests.open(newline="", encoding="utf-8") as fh:
            for index, row in enumerate(csv.reader(fh), start=1):
                if index == 1 or len(row) < 5:
                    continue
                if not THREE_DECIMALS.match(row[4]):
                    failures.append(f"tests.csv row {index}: time {row[4]!r} is not 3 decimals")

    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "tests": 10,
            "passed": 4,
            "failed": 3,
            "errored": 2,
            "skipped": 1,
            "time": 4.105,
            "slowest": "test_four",
        },
    )
    return failures
