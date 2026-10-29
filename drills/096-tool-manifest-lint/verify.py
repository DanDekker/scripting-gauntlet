"""Grader for 096-tool-manifest-lint."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "errors.csv",
        ["tool", "code"],
        [
            ("ReadURL", "bad-name"),
            ("Send Email", "bad-name"),
            ("Send Email", "no-description"),
            ("Send Email", "no-parameters"),
            ("delete_workspace", "no-description"),
            ("delete_workspace", "undeclared-required"),
            ("describe_image", "no-description"),
            ("fetch_url", "no-properties"),
            ("get_time", "no-properties"),
            ("list_dir", "undeclared-required"),
            ("log_event", "duplicate-key"),
            ("parse_config", "no-parameters"),
            ("run_shell", "duplicate-key"),
            ("run_shell", "no-parameters"),
            ("search_web", "no-parameters"),
            ("write_file", "required-not-declared"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"tools": 13, "valid_tools": 1, "invalid_tools": 12, "errors": 16},
    )
    return failures
