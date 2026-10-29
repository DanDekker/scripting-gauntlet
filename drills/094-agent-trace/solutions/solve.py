#!/usr/bin/env python3
"""Summarise an agent trace: skip junk lines, split billed from cached, group by tool."""

import json
import os
from pathlib import Path


def load_records(path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or "tool" not in obj:
            continue
        records.append(obj)
    return records


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    records = load_records(in_dir / "trace.jsonl")

    per_tool = {}
    total_tokens = 0
    cached_tokens = 0
    error_turns = 0

    for record in records:
        tool = record["tool"]
        tokens = int(record.get("tokens") or 0)
        cached = record.get("cached") is True
        is_error = record.get("error") is not None

        billed = 0 if cached else tokens
        total_tokens += billed
        if cached:
            cached_tokens += tokens
        if is_error:
            error_turns += 1

        stats = per_tool.setdefault(tool, {"calls": 0, "errors": 0, "tokens": 0})
        stats["calls"] += 1
        stats["tokens"] += billed
        if is_error:
            stats["errors"] += 1

    tools = sorted(per_tool)
    rows = ["tool,calls,errors,tokens"]
    for tool in tools:
        stats = per_tool[tool]
        rows.append(f"{tool},{stats['calls']},{stats['errors']},{stats['tokens']}")
    (out_dir / "tools.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    most_called = ""
    if tools:
        most_called = sorted(tools, key=lambda tool: (-per_tool[tool]["calls"], tool))[0]

    summary = {
        "turns": len(records),
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "error_turns": error_turns,
        "most_called_tool": most_called,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
