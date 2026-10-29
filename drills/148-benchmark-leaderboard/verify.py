"""Grader for 148-benchmark-leaderboard."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "leaderboard.csv",
        ["rank", "model", "composite_score"],
        [
            (1, "gpt-4o", 0.8449),
            (2, "llama-3", 0.8106),
            (3, "claude-3-5", 0.7316),
            (4, "zeta-model", 0.7316),
            (5, "o3-mini", 0.6667),
            (6, "deepseek-v2", 0.3095),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_models": 9,
            "complete_models": 6,
            "incomplete_models": 3,
            "top_model": "gpt-4o",
            "winning_score": 0.8449,
        },
    )
    return failures
