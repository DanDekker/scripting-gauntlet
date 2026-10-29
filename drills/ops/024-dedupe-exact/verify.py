"""Grader for 024-dedupe-exact."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "deduped.csv",
        ["email", "name", "plan", "signed_up"],
        [
            ("dana@example.com", "Dana Reed", "pro", "2026-01-04"),
            ("ali@example.com", "Ali Khan", "free", "2026-01-11"),
            ("bo@example.com", "Bo Lin", "team", "2026-02-02"),
            ("dana@example.com", "Dana Reed", "PRO", "2026-01-04"),
            ("cy@example.com", "Cy Okafor", "free", "2026-02-09"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"rows_in": 9, "unique": 5, "dropped": 4}
    )
    return failures
