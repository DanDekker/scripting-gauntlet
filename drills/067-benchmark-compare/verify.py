"""Grader for 067-benchmark-compare."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "comparison.csv",
        ["platform", "case", "baseline_median_ms", "candidate_median_ms", "change_pct", "status"],
        [
            ("linux", "gzip", 20.0, 24.0, 20.0, "regression"),
            ("linux", "json", 10.0, 10.8, 8.0, "ok"),
            ("macos", "json", 15.0, 12.0, -20.0, "ok"),
            ("windows", "json", 30.0, 33.0, 10.0, "ok"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"comparisons": 4, "regressions": 1, "threshold_pct": 10}
    )
    return failures
