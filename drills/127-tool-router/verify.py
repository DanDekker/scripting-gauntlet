"""Grader for 127-tool-router."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "routes.csv",
        ["id", "tool", "matched"],
        [
            ("r1", "search_code", 1),
            ("r2", "web_search", 2),
            ("r3", "search_code", 1),
            ("r4", "", 0),
            ("r5", "read_file", 1),
            ("r6", "", 0),
            ("r7", "read_file", 1),
            ("r8", "run_tests", 2),
            ("r9", "", 0),
            ("r10", "", 0),
            ("r11", "", 0),
            ("r12", "read_file", 1),
            ("r13", "compile_cpp", 1),
            ("r14", "read_file", 2),
            ("dup", "search_code", 1),
            ("dup", "search_code", 1),
            ("r17", "", 0),
            ("r22", "web_search", 1),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "requests": 18,
            "routed": 12,
            "unrouted": 6,
            "by_tool": {
                "compile_cpp": 1,
                "read_file": 4,
                "run_tests": 1,
                "search_code": 4,
                "web_search": 2,
            },
        },
    )
    return failures
