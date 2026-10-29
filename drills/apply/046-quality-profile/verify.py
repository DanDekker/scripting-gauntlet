"""Grader for 046-quality-profile."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "profile.csv",
        ["column", "non_null", "nulls", "distinct", "numeric", "min", "max", "top_value", "top_count"],
        [
            ("country", 9, 1, 2, "no", "", "", "US", 7),
            ("customer_id", 10, 0, 10, "yes", 1.00, 10.00, "1", 1),
            ("email", 8, 2, 8, "no", "", "", "ada@example.com", 1),
            ("ltv", 10, 0, 5, "yes", 0.00, 1250.00, "0.00", 5),
            ("notes", 2, 8, 2, "no", "", "", "churn risk", 1),
            ("segment", 8, 2, 2, "no", "", "", "pro", 4),
            ("signup_date", 9, 1, 9, "no", "", "", "2026-01-04", 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"rows": 10, "columns": 7, "nulls": 14, "worst_column": "notes", "worst_nulls": 8},
    )
    return failures
