#!/usr/bin/env python3
"""Grade RAG cases: retrieval, groundedness and answer relevance, then one issue label."""

import json
import os
from pathlib import Path


def text(value):
    return value if isinstance(value, str) else ""


def keywords(value):
    if not isinstance(value, list):
        return []
    return [text(item).strip().lower() for item in value]


def load_cases(path):
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or not isinstance(obj.get("case_id"), str):
            continue
        cases.append(obj)
    return cases


def score(case):
    context = text(case.get("context")).lower()
    answer = text(case.get("answer")).lower()
    ground_truth = text(case.get("ground_truth")).strip().lower()
    context_keywords = keywords(case.get("context_keywords"))
    answer_keywords = keywords(case.get("answer_keywords"))

    hits = sum(1 for word in context_keywords if word in context)
    context_rel = 1 if not context_keywords or hits * 2 >= len(context_keywords) else 0
    grounded = 1 if all(word in context for word in answer_keywords) else 0
    answer_rel = 1 if ground_truth and ground_truth in answer else 0

    if context_rel == 0:
        issue = "bad_retrieval"
    elif grounded == 0:
        issue = "hallucination"
    elif answer_rel == 0:
        issue = "poor_answer"
    else:
        issue = "none"
    verdict = "pass" if context_rel == grounded == answer_rel == 1 else "fail"
    return context_rel, grounded, answer_rel, verdict, issue


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for case in load_cases(in_dir / "rag_cases.jsonl"):
        context_rel, grounded, answer_rel, verdict, issue = score(case)
        rows.append((case["case_id"], context_rel, grounded, answer_rel, verdict, issue))
    rows.sort(key=lambda row: row[0])

    lines = ["case_id,context_rel,grounded,answer_rel,verdict,issue"]
    lines += [",".join(str(cell) for cell in row) for row in rows]
    (out_dir / "eval.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    passed = sum(1 for row in rows if row[4] == "pass")
    summary = {
        "total_cases": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "pass_rate": round(passed / len(rows), 4) if rows else 0.0,
        "hallucinations": sum(1 for row in rows if row[5] == "hallucination"),
        "bad_retrievals": sum(1 for row in rows if row[5] == "bad_retrieval"),
        "poor_answers": sum(1 for row in rows if row[5] == "poor_answer"),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
