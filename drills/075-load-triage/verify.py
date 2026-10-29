"""Grader for 075-load-triage."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "triage.csv",
        ["host", "verdict", "load1_per_cpu", "r_avg", "wa_avg", "busy_pct"],
        [
            ("cache01", "memory", 4.55, 2.0, 6.0, 18.0),
            ("db01", "io", 1.55, 3.0, 42.0, 18.0),
            ("idle01", "healthy", 0.05, 0.0, 0.0, 5.0),
            ("web01", "cpu", 2.00, 9.0, 2.0, 95.3),
        ],
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"hosts": 4, "saturated": 3})
    return failures
