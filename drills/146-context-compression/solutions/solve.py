#!/usr/bin/env python3
"""Compress a chat transcript into a structured memory summary."""

import json
import os
from pathlib import Path


def text(value):
    return value if isinstance(value, str) else ""


def line_count(value):
    if value == "":
        return 0
    parts = value.split("\n")
    if parts[-1] == "":
        parts.pop()
    return len(parts)


def compress(tool, output):
    if tool == "read_file":
        return f"[READ: {line_count(output)} lines, {len(output)} chars]"
    if tool == "edit_file":
        return "[EDIT: ok]" if "Successfully" in output else "[EDIT: failed]"
    if tool == "bash":
        if len(output) > 100:
            return output[:50] + "...[truncated]..." + output[-50:]
        return output
    if len(output) > 100:
        return output[:100] + "..."
    return output


def load_messages(path):
    messages = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        idx = record.get("idx")
        if isinstance(idx, bool) or not isinstance(idx, (int, float)):
            continue
        if isinstance(idx, float):
            if not idx.is_integer():
                continue
            idx = int(idx)
        role = record.get("role")
        if not isinstance(role, str):
            continue
        messages.append((idx, role, record))
    messages.sort(key=lambda message: message[0])
    return messages


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    messages = load_messages(in_dir / "transcript.jsonl")

    lines = []
    original_chars = 0
    compressed_chars = 0
    tool_messages = 0

    for idx, role, record in messages:
        if role == "tool":
            tool_messages += 1
            tool = text(record.get("tool"))
            raw = text(record.get("output"))
            new = compress(tool, raw)
            original_chars += len(raw)
            compressed_chars += len(new)
            body = {"idx": idx, "role": role, "tool": tool, "output": new}
        else:
            new = text(record.get("content"))
            original_chars += len(new)
            compressed_chars += len(new)
            body = {"idx": idx, "role": role, "content": new}
        lines.append(json.dumps(body, ensure_ascii=False, separators=(",", ":")))

    (out_dir / "compressed.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    ratio = 0.0 if original_chars == 0 else compressed_chars / original_chars
    summary = {
        "total_messages": len(messages),
        "tool_messages": tool_messages,
        "original_chars": original_chars,
        "compressed_chars": compressed_chars,
        "saved_chars": original_chars - compressed_chars,
        "compression_ratio": float(f"{ratio:.4f}"),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
