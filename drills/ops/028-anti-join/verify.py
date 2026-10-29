"""Grader for 028-anti-join."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "inactive.csv",
        ["customer_id", "name"],
        [
            ("c-01", "Acme"),
            ("c-03", "Gamma"),
            ("c-04", "Delta"),
            ("c-05", "Epsilon"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"customers": 5, "active": 1, "inactive": 4}
    )
    return failures
