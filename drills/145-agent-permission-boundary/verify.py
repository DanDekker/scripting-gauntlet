"""Grader for 145-agent-permission-boundary."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "audit.csv",
        ["id", "tool", "verdict", "violations"],
        [
            ("inv-1", "read_file", "allowed", ""),
            ("inv-10", "read_file", "allowed", ""),
            ("inv-11", "read_file", "allowed", ""),
            ("inv-12", "bash", "allowed", ""),
            ("inv-13", "http_get", "denied", "disallowed-domain"),
            ("inv-14", "read_file", "denied", "path-traversal"),
            ("inv-15", "bash", "denied", "banned-command"),
            ("inv-16", "curl", "denied", "unknown-tool"),
            ("inv-17", "bash", "allowed", ""),
            ("inv-18", "", "denied", "path-traversal;unknown-tool"),
            ("inv-19", "http_get", "denied", "disallowed-domain"),
            ("inv-2", "bash", "denied", "banned-command"),
            ("inv-20", "bash", "denied", "banned-command"),
            ("inv-21", "bash", "denied", "banned-command"),
            ("inv-22", "read_file", "denied", "path-traversal"),
            ("inv-23", "bash", "denied", "banned-command;path-traversal"),
            ("inv-3", "http_get", "allowed", ""),
            ("inv-4", "read_file", "denied", "path-traversal"),
            ("inv-5", "http_get", "denied", "disallowed-domain"),
            ("inv-6", "exec_shell", "denied", "unknown-tool"),
            ("inv-7", "http_get", "allowed", ""),
            ("inv-8", "bash", "allowed", ""),
            ("inv-9", "write_file", "denied", "path-traversal"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_invocations": 23,
            "allowed_count": 8,
            "denied_count": 15,
            "violations_count": 17,
        },
    )
    return failures
