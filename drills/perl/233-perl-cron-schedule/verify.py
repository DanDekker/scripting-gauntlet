"""Grader for 233-perl-cron-schedule.

Verifies cron expression matching across minute, hour, dom, mon, dow.
"""

import verifylib

EXPECTED_LINES = [
    "/opt/scripts/healthcheck.sh --quick",
    "/opt/scripts/midday-sweep.sh",
    "/opt/scripts/late-october-weekday.sh",
]

EXPECTED_SUMMARY = {"total_entries": 11, "matched": 3}


def verify(io):
    failures = verifylib.lines(io.out / "matched.txt", EXPECTED_LINES)
    failures += verifylib.json_eq(io.out / "summary.json", EXPECTED_SUMMARY)
    return failures
