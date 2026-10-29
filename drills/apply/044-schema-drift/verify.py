"""Grader for 044-schema-drift."""

import verifylib

DAYS = ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01"]


def verify(io):
    failures = verifylib.table(
        io.out / "columns.csv",
        ["column", "first_seen", "last_seen", "files_present", "status"],
        [
            ("amount", "2026-09-28.csv", "2026-09-30.csv", 3, "dropped"),
            ("currency", "2026-09-28.csv", "2026-10-01.csv", 4, "stable"),
            ("customer", "2026-09-28.csv", "2026-10-01.csv", 4, "stable"),
            ("order_id", "2026-09-28.csv", "2026-10-01.csv", 4, "stable"),
            ("placed_at", "2026-09-28.csv", "2026-10-01.csv", 4, "stable"),
            ("region", "2026-09-29.csv", "2026-10-01.csv", 3, "added"),
            ("promo_code", "2026-09-30.csv", "2026-09-30.csv", 1, "transient"),
            ("amount_usd", "2026-10-01.csv", "2026-10-01.csv", 1, "added"),
        ],
    )
    failures += verifylib.table(
        io.out / "types.csv",
        ["column"] + DAYS + ["drift"],
        [
            ("amount", "float", "float", "int", "absent", "yes"),
            ("amount_usd", "absent", "absent", "absent", "float", "no"),
            ("currency", "text", "text", "text", "text", "no"),
            ("customer", "text", "text", "text", "text", "no"),
            ("order_id", "int", "int", "int", "int", "no"),
            ("placed_at", "text", "text", "text", "text", "no"),
            ("promo_code", "absent", "absent", "text", "absent", "no"),
            ("region", "absent", "text", "text", "text", "no"),
        ],
    )
    failures += verifylib.table(
        io.out / "files.csv",
        ["file", "rows", "columns"],
        [
            ("2026-09-28.csv", 3, 5),
            ("2026-09-29.csv", 2, 6),
            ("2026-09-30.csv", 2, 7),
            ("2026-10-01.csv", 3, 6),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files": 4,
            "columns": 8,
            "rows": 10,
            "stable": 4,
            "added": 2,
            "dropped": 1,
            "transient": 1,
            "type_drift": 1,
        },
    )
    return failures
