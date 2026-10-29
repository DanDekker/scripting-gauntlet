#!/usr/bin/env python3
"""Attribute LLM spend per project and role, flagging unpriced models and budgets."""

import json
import os
from pathlib import Path


def load_rates(path):
    """model -> (prompt_per_1k, completion_per_1k); header and junk rows skipped."""
    rates = {}
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if index == 0:
            continue
        cells = [cell.strip() for cell in line.split(",")]
        if len(cells) < 3 or not cells[0]:
            continue
        try:
            rates[cells[0]] = (float(cells[1]), float(cells[2]))
        except ValueError:
            continue
    return rates


def as_tokens(value):
    """A token count is a non-negative JSON integer, and nothing else."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def as_text(value):
    return value.strip() if isinstance(value, str) else ""


def load_records(path):
    """Every line that parses to a JSON object, valid turn or not."""
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    rates = load_rates(in_dir / "pricing.csv")
    budgets = json.loads((in_dir / "budgets.json").read_text(encoding="utf-8"))
    records = load_records(in_dir / "sessions.jsonl")

    turns = []
    for record in records:
        turn = {
            "session": as_text(record.get("session_id")),
            "project": as_text(record.get("project")),
            "role": as_text(record.get("role")),
            "model": as_text(record.get("model")),
            "prompt_tokens": as_tokens(record.get("prompt_tokens")),
            "completion_tokens": as_tokens(record.get("completion_tokens")),
            "success": record.get("success") is True,
        }
        if (
            not turn["session"]
            or not turn["project"]
            or not turn["role"]
            or not turn["model"]
            or turn["prompt_tokens"] is None
            or turn["completion_tokens"] is None
        ):
            continue
        rate = rates.get(turn["model"])
        turn["unpriced"] = rate is None
        if rate is None:
            turn["cost"] = 0.0
        else:
            prompt_rate, completion_rate = rate
            turn["cost"] = round(
                (turn["prompt_tokens"] / 1000.0) * prompt_rate
                + (turn["completion_tokens"] / 1000.0) * completion_rate,
                6,
            )
        turns.append(turn)

    total_spend = sum(turn["cost"] for turn in turns)

    projects = {}
    roles = {}
    sessions = {}
    for turn in turns:
        projects.setdefault(turn["project"], []).append(turn)
        roles.setdefault(turn["role"], []).append(turn)
        sessions.setdefault(turn["session"], []).append(turn)

    project_lines = ["project,turns,cost,budget,over_budget"]
    over_budget = 0
    for name in sorted(projects):
        group = projects[name]
        cost = sum(turn["cost"] for turn in group)
        limit = budgets.get(name)
        is_over = limit is not None and cost > limit
        over_budget += 1 if is_over else 0
        project_lines.append(
            ",".join(
                [
                    name,
                    str(len(group)),
                    f"{cost:.4f}",
                    "" if limit is None else f"{float(limit):.4f}",
                    "true" if is_over else "false",
                ]
            )
        )
    (out_dir / "projects.csv").write_text("\n".join(project_lines) + "\n", encoding="utf-8")

    role_lines = ["role,turns,cost,pct_spend"]
    for name in sorted(roles):
        group = roles[name]
        cost = sum(turn["cost"] for turn in group)
        pct = (cost / total_spend * 100.0) if total_spend else 0.0
        role_lines.append(",".join([name, str(len(group)), f"{cost:.4f}", f"{pct:.2f}"]))
    (out_dir / "roles.csv").write_text("\n".join(role_lines) + "\n", encoding="utf-8")

    summary = {
        "total_turns": len(records),
        "valid_turns": len(turns),
        "unpriced_turns": sum(1 for turn in turns if turn["unpriced"]),
        "total_spend": round(total_spend, 4),
        "over_budget_projects": over_budget,
        "successful_sessions": sum(
            1 for group in sessions.values() if all(turn["success"] for turn in group)
        ),
        "total_sessions": len(sessions),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
