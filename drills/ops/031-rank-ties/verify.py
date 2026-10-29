"""Grader for 031-rank-ties."""

import verifylib


def verify(io):
    failures = verifylib.table(
        io.out / "ranked.csv",
        ["name", "score", "rank", "dense_rank"],
        [
            ("Ana", 91, 1, 1),
            ("Cyd", 91, 1, 1),
            ("Ben", 88, 3, 2),
            ("Eli", 88, 3, 2),
            ("Fay", 88, 3, 2),
            ("Dee", 75, 6, 3),
            ("Gus", 60, 7, 4),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json", {"players": 7, "top_score": 91, "distinct_scores": 4}
    )
    return failures
