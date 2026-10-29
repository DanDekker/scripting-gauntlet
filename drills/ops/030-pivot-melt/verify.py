"""Grader for 030-pivot-melt."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "long.csv",
        ["region", "quarter", "amount"],
        [
            ("east", "q1", 0.0),
            ("east", "q2", 80.0),
            ("east", "q3", 15.0),
            ("east", "q4", 5.0),
            ("north", "q1", 100.0),
            ("north", "q2", 50.0),
            ("north", "q4", 25.0),
            ("south", "q1", 10.0),
            ("south", "q3", 30.0),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"regions": 3, "cells": 9, "total": 315.0}
    )
    return failures
