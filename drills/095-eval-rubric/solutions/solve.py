#!/usr/bin/env python3
"""Score eval cases: pick a matcher per kind, and fail what cannot be judged."""

import json
import os
from pathlib import Path

NUMBER_TOLERANCE = 0.01


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
        if not isinstance(obj, dict):
            continue
        cases.append(obj)
    return cases


def text(value):
    return "" if value is None else str(value).strip()


def as_number(value):
    try:
        return float(text(value))
    except ValueError:
        return None


def passed(case):
    expected = text(case.get("expected"))
    actual = text(case.get("actual"))
    kind = case.get("kind")
    if kind == "exact":
        return expected == actual
    if kind == "contains":
        return expected.lower() in actual.lower()
    if kind == "number":
        left, right = as_number(expected), as_number(actual)
        if left is None or right is None:
            return False
        return abs(left - right) <= NUMBER_TOLERANCE
    return False


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = load_cases(in_dir / "cases.jsonl")

    rows = ["id,kind,passed"]
    total = 0
    score = 0
    for case in cases:
        ok = passed(case)
        total += 1
        score += 1 if ok else 0
        rows.append(f"{text(case.get('id'))},{text(case.get('kind'))},{'true' if ok else 'false'}")
    (out_dir / "scores.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    summary = {
        "total": total,
        "passed": score,
        "failed": total - score,
        "pass_rate": round(score / total, 4) if total else 0.0,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
