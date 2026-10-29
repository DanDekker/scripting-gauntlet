"""Grader for 072-cron-expand."""

import verifylib

ALL_DOW = list(range(7))
ALL_MONTH = list(range(1, 13))
ALL_DOM = list(range(1, 32))


def verify(io):
    failures = verifylib.json_eq(
        io.out / "schedule.json",
        {
            "backup": {
                "minute": [0],
                "hour": [3],
                "dom": ALL_DOM,
                "month": ALL_MONTH,
                "dow": ALL_DOW,
            },
            "poll": {
                "minute": [0, 15, 30, 45],
                "hour": list(range(9, 18)),
                "dom": ALL_DOM,
                "month": ALL_MONTH,
                "dow": [1, 2, 3, 4, 5],
            },
            "weekly": {
                "minute": [30],
                "hour": [6],
                "dom": ALL_DOM,
                "month": ALL_MONTH,
                "dow": [0],
            },
            "cleanup": {
                "minute": [0],
                "hour": [0],
                "dom": [1],
                "month": [1, 7],
                "dow": ALL_DOW,
            },
            "flush": {
                "minute": [5, 15, 25],
                "hour": list(range(24)),
                "dom": ALL_DOM,
                "month": ALL_MONTH,
                "dow": ALL_DOW,
            },
        },
    )
    failures += verifylib.json_eq(io.out / "summary.json", {"jobs": 5, "slots": 111})
    return failures
