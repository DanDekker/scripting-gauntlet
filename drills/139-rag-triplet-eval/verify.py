"""Grader for 139-rag-triplet-eval."""

import verifylib


def verify(io) -> list[str]:
    failures = verifylib.table(
        io.out / "eval.csv",
        ["case_id", "context_rel", "grounded", "answer_rel", "verdict", "issue"],
        [
            ("rag-1", 1, 0, 0, "fail", "hallucination"),
            ("rag-10", 1, 1, 1, "pass", "none"),
            ("rag-2", 0, 0, 0, "fail", "bad_retrieval"),
            ("rag-3", 1, 1, 0, "fail", "poor_answer"),
            ("rag-4", 1, 1, 1, "pass", "none"),
            ("rag-5", 1, 1, 0, "fail", "poor_answer"),
            ("rag-6", 1, 1, 0, "fail", "poor_answer"),
            ("rag-7", 1, 1, 1, "pass", "none"),
            ("rag-8", 1, 1, 1, "pass", "none"),
            ("rag-9", 0, 1, 1, "fail", "bad_retrieval"),
        ],
    )
    failures += verifylib.json_eq(
        io.out / "summary.json",
        {
            "total_cases": 10,
            "passed": 4,
            "failed": 6,
            "pass_rate": 0.4,
            "hallucinations": 1,
            "bad_retrievals": 2,
            "poor_answers": 3,
        },
    )
    return failures
