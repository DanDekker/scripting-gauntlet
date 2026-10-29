#!/usr/bin/env python3
"""Detect loops in an agent action trace: maximal period-1/2/3 runs, greedy left to right."""

import json
import os
from pathlib import Path


def canonical(tool, args):
    """tool plus args JSON with every key sorted and no whitespace."""
    return tool + ":" + json.dumps(args, sort_keys=True, separators=(",", ":"))


def load_actions(path):
    actions = []
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
        step, tool = obj.get("step"), obj.get("tool")
        if not isinstance(step, (int, float)) or isinstance(step, bool):
            continue
        if not isinstance(tool, str):
            continue
        args = obj.get("args")
        if not isinstance(args, dict):
            args = {}
        actions.append({"step": step, "tool": tool, "key": canonical(tool, args)})
    actions.sort(key=lambda action: action["step"])
    return actions


def detect(actions):
    keys = [action["key"] for action in actions]
    tools = [action["tool"] for action in actions]
    steps = [action["step"] for action in actions]
    n = len(keys)
    loops = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and keys[j + 1] == keys[i]:
            j += 1
        if j - i + 1 >= 3:
            loops.append(
                (steps[i], steps[j], "repeat_action", f"{tools[i]} repeated {j - i + 1}x")
            )
            i = j + 1
            continue

        # Longest period-2 span: every m in [i, j-2] must repeat two steps later.
        j, m = i - 1, i
        while m + 2 < n and keys[m] == keys[m + 2]:
            j, m = m + 2, m + 1
        if j - i + 1 >= 6:
            loops.append(
                (
                    steps[i],
                    steps[j],
                    "cycle_2",
                    f"{tools[i]} <-> {tools[i + 1]} x{(j - i + 1) // 2}",
                )
            )
            i = j + 1
            continue

        j, m = i - 1, i
        while m + 3 < n and keys[m] == keys[m + 3]:
            j, m = m + 3, m + 1
        if j - i + 1 >= 6:
            loops.append(
                (
                    steps[i],
                    steps[j],
                    "cycle_3",
                    f"{tools[i]} -> {tools[i + 1]} -> {tools[i + 2]} x{(j - i + 1) // 3}",
                )
            )
            i = j + 1
            continue

        i += 1
    return loops


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    actions = load_actions(in_dir / "actions.jsonl")
    loops = detect(actions)

    lines = ["start_step,end_step,pattern_type,description"]
    lines += [",".join(str(cell) for cell in loop) for loop in loops]
    (out_dir / "loops.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "total_steps": len(actions),
        "status": "looping" if loops else "healthy",
        "loop_count": len(loops),
        "first_loop_step": loops[0][0] if loops else None,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
