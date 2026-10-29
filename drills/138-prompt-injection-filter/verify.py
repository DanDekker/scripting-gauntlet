"""Grader for 138-prompt-injection-filter."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "screened.csv",
        ["id", "source", "verdict", "flags"],
        [
            ("msg-001", "user", "clean", ""),
            ("msg-002", "user", "flagged", "override"),
            ("msg-003", "tool", "flagged", "base64-payload"),
            ("msg-004", "user", "flagged", "override;zero-width"),
            ("msg-005", "tool", "flagged", "exfiltration"),
            ("msg-006", "user", "flagged", "delimiter-spoof;override"),
            ("msg-007", "user", "flagged", "delimiter-spoof"),
            ("msg-008", "tool", "clean", ""),
            ("msg-009", "user", "flagged", "override"),
            ("msg-010", "tool", "flagged", "delimiter-spoof"),
            ("msg-011", "user", "clean", ""),
            ("msg-012", "user", "flagged", "override"),
            ("msg-013", "user", "flagged", "override"),
            ("msg-014", "tool", "flagged", "zero-width"),
            ("msg-015", "", "clean", ""),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_inputs": 15,
            "clean_count": 4,
            "flagged_count": 11,
            "by_flag": {
                "base64-payload": 1,
                "delimiter-spoof": 3,
                "exfiltration": 1,
                "override": 6,
                "zero-width": 2,
            },
        },
    )
    return failures
