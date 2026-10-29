"""Grader for 118-mcp-config."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "problems.csv",
        ["server", "problem", "detail"],
        [
            ("Bad Args", "bad-name", ""),
            ("Bad Args", "bad-args", ""),
            ("Blank", "bad-name", ""),
            ("Blank", "empty-command", ""),
            ("db", "undefined-env", "MISSING_VAR"),
            ("db", "undefined-env", "OTHER_MISSING"),
            ("dup", "duplicate-name", "duplicate"),
            ("empty", "empty-command", ""),
            ("extra", "unknown-key", "autostart"),
            ("extra", "unknown-key", "cwd"),
            ("ghost", "missing-command", ""),
            ("numargs", "bad-args", ""),
            ("shell", "unknown-key", "autostart"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"servers": 12, "valid": 3, "invalid": 9, "problems": 13},
    )
    return failures
