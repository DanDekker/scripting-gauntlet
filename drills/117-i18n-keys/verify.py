"""Grader for 117-i18n-keys."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "keys.csv",
        ["file", "line", "key", "status"],
        [
            ("app.js", 2, "app.title", "present"),
            ("app.js", 5, "app.welcome", "present"),
            ("app.js", 6, "button.close", "present"),
            ("app.js", 9, "app.fresh", "missing"),
            ("header.js", 2, "header.tagline", "present"),
            ("header.js", 3, "header.tagline", "present"),
            ("header.js", 4, "nav.help", "present"),
            ("header.js", 8, "header.hint", "missing"),
            ("legacy.py", 3, "legacy.count", "present"),
            ("legacy.py", 4, "app.title", "present"),
            ("ui/modal.js", 1, "ui.brand", "present"),
            ("ui/modal.js", 2, "ui.subtitle", "missing"),
            ("ui/modal.js", 3, "button.save", "present"),
        ],
    )
    failures += verifylib.table(
        io.out / "unused.csv",
        ["key", "reason"],
        [("orphan.key", "unused"), ("zzz.orphan", "unused")],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"files": 5, "calls": 13, "distinct": 11, "missing": 3, "unused": 2, "invalid": 2},
    )
    return failures
