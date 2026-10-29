"""Grader for 102-secret-scan."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "findings.csv",
        ["file", "line", "key", "value"],
        [
            ("app/client.py", 3, "api_key", "sk_live_9f8a7b6c5d4e3f21"),
            ("app/config.py", 2, "API_KEY", "sk_live_9f8a7b6c5d4e3f21"),
            ("app/config.py", 4, "PASSWORD", "hunter2hunter2"),
            ("app/legacy.ini", 3, "api_key", "legacy-key-0001"),
            ("deploy/ci.yml", 3, "Secret", "ci_9f8f8f8f8f8f"),
            ("deploy/ci.yml", 4, "TOKEN", "ghp_0123456789abcdef0123456789abcdef"),
            ("deploy/notes.txt", 2, "password", "correct horse battery staple"),
            ("scripts/setup.sh", 3, "API_KEY", "sk_test_commentleak123"),
            ("scripts/setup.sh", 4, "TOKEN", "s3cr3t-token-value"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "files_scanned": 9,
            "candidates": 18,
            "secrets": 9,
            "unique_values": 8,
            "sample_files": 2,
        },
    )
    return failures
