"""Grader for 108-redact-output."""

import verifylib

REDACTED = [
    "api_key = [REDACTED]",
    "[2024-05-02T10:00:01Z] INFO  loaded config from /etc/app.toml",
    "[2024-05-02T10:00:02Z] WARN  contact [EMAIL] for approval",
    "password: [REDACTED]",
    "secret =",
    'token = ""',
    "apikey=[REDACTED]",
    "authorization: [REDACTED]",
    "commit 3f9a7c1d2e4b5a6978c0d1e2f3a4b5c6d7e8f901",
    "card on file [CARD] expires 12/27",
    "backup card [CARD]",
    "order id 123456789012 shipped",
    "legacy record 12345678901234567890 rejected",
    "api_key = [REDACTED]",
    "user=bob token: [REDACTED] password=[REDACTED]",
    "password: [REDACTED]",
    "api_key = REDACTED",
    "password = ****",
    "token = xxxxx",
    "secret = abc12",
    "api_key = [REDACTED]",
    "7b6c5d4e3f2a1b",
    "[2024-05-02T10:00:03Z] ERROR upstream 502 from https://api.internal/v1/items?token=[REDACTED]",
    "access_key = [REDACTED]",
]


def verify(io) -> list[str]:
    failures = verifylib.lines(io.out / "redacted.txt", REDACTED, "redacted.txt")

    redacted = io.out / "redacted.txt"
    source = io.inp / "output.txt"
    if redacted.is_file() and source.is_file():
        got = redacted.read_bytes()
        was = source.read_bytes()
        if got.endswith(b"\n") and not was.endswith(b"\n"):
            failures.append("redacted.txt: input has no trailing newline, output must not either")
        if len(got.split(b"\n")) != len(was.split(b"\n")):
            failures.append("redacted.txt: line count must match the input, no line added or dropped")

    failures += verifylib.json_eq(
        io.out / "summary.json",
        {"lines": 24, "secrets": 11, "emails": 1, "cards": 2, "changed": 13},
    )
    return failures
