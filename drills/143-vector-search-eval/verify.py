"""Grader for 143-vector-search-eval."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "metrics.csv",
        ["qid", "k", "hits", "recall", "mrr"],
        [
            ("q1", 3, 2, "0.6667", "1.0000"),
            ("q2", 2, 2, "1.0000", "1.0000"),
            ("q3", 2, 1, "0.5000", "0.5000"),
            ("q4", 2, 1, "0.5000", "0.5000"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "queries": 4,
            "corpus_size": 9,
            "avg_recall": 0.6667,
            "mean_mrr": 0.75,
        },
    )
    return failures
