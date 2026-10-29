"""Grader for 112-jwt-claims."""

import verifylib


TOKENS = [
    ("1", "valid", "user-alice", 1793296800),
    ("3", "expired", "user-carol", 1793271600),
    ("4", "malformed", "", ""),
    ("5", "valid", "svc-cron", 1793278800),
    ("6", "none-alg", "anon-write", 1793278800),
    ("7", "not-yet-valid", "future-user", 1793282400),
    ("8", "valid", "forever", ""),
    ("9", "valid", "string-exp", ""),
    ("10", "valid", "paddedx", 1793276100),
    ("11", "valid", "", 1793275800),
    ("12", "expired", "both-bad", 1793274600),
    ("13", "valid", "case-alg", 1793275800),
    ("14", "expired", "trailing", 1793275140),
    ("15", "malformed", "", ""),
    ("16", "valid", "user-bob", 1793361600),
]


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "tokens.csv", ["index", "status", "sub", "exp"], TOKENS
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "tokens": 15,
            "malformed": 2,
            "none_alg": 1,
            "expired": 3,
            "not_yet_valid": 1,
            "valid": 8,
            "subjects": 12,
        },
    )
    return failures
