#!/usr/bin/env python3
"""Find the flaky tests: a pass and a failure are both required."""

import json
import os
from pathlib import Path


def load_runs(path):
    runs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        name = obj.get("test")
        if not isinstance(name, str) or not name.strip():
            continue
        runs.append({"test": name.strip(), "passed": passed(obj.get("passed"))})
    return runs


def passed(value):
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = load_runs(in_dir / "history.jsonl")

    stats = {}
    for run in runs:
        entry = stats.setdefault(run["test"], {"total": 0, "passed": 0, "failed": 0})
        entry["total"] += 1
        entry["passed" if run["passed"] else "failed"] += 1

    flaky = []
    stable_pass = 0
    stable_fail = 0
    for name in sorted(stats):
        entry = stats[name]
        if entry["passed"] and entry["failed"]:
            flaky.append((name, entry))
        elif entry["passed"]:
            stable_pass += 1
        else:
            stable_fail += 1

    lines = ["test,total,passed,failed,fail_rate"]
    for name, entry in flaky:
        rate = f"{entry['failed'] / entry['total']:.4f}"
        lines.append(
            f"{name},{entry['total']},{entry['passed']},{entry['failed']},{rate}"
        )
    (out_dir / "flaky.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "tests": len(stats),
        "flaky": len(flaky),
        "stable_pass": stable_pass,
        "stable_fail": stable_fail,
        "runs": len(runs),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
