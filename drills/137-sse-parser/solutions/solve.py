#!/usr/bin/env python3
"""Rebuild a chat completion from a captured SSE stream."""

import json
import os
from pathlib import Path

DONE = "[DONE]"


def split_events(text):
    """Split a raw SSE body into event blocks, keeping comment counts and data fields."""
    events = []
    comments = 0
    data = []
    started = False

    def flush():
        nonlocal comments, data, started
        if started:
            events.append({"comments": comments, "data": data})
        comments = 0
        data = []
        started = False

    for raw in text.splitlines():
        line = raw.rstrip()  # trailing spaces, tabs and the CR of a CRLF capture
        if not line:
            flush()
            continue
        started = True
        if line.startswith(":"):
            comments += 1
            continue
        name, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if name == "data":
            data.append(value)
    flush()
    return events


def token_count(usage, key):
    value = usage.get(key) if isinstance(usage, dict) else None
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    events = split_events((in_dir / "stream.txt").read_text(encoding="utf-8"))

    message = []
    chunks = []
    comment_lines = 0
    malformed = 0
    completed = False
    prompt_tokens = 0
    completion_tokens = 0

    for event in events:
        comment_lines += event["comments"]
        if not event["data"]:
            continue
        payload = "\n".join(event["data"])
        if payload == DONE:
            completed = True
            continue
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not isinstance(obj, dict):
            continue

        usage = obj.get("usage")
        if isinstance(usage, dict):
            prompt_tokens = token_count(usage, "prompt_tokens")
            completion_tokens = token_count(usage, "completion_tokens")

        choices = obj.get("choices")
        if not isinstance(choices, list) or not choices:
            continue
        delta = choices[0].get("delta") if isinstance(choices[0], dict) else None
        delta = delta if isinstance(delta, dict) else {}
        content = delta.get("content")
        role = delta.get("role")
        if isinstance(content, str):
            message.append(content)
            delta_len = len(content)
        else:
            delta_len = 0
        chunks.append((delta_len, role if isinstance(role, str) else ""))

    text = "".join(message)
    (out_dir / "message.txt").write_text(text + "\n" if text else "", encoding="utf-8")

    rows = ["chunk_index,delta_len,role"]
    for index, (delta_len, role) in enumerate(chunks, start=1):
        rows.append(f"{index},{delta_len},{role}")
    (out_dir / "chunks.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")

    summary = {
        "total_events": len(events),
        "comment_lines": comment_lines,
        "valid_chunks": len(chunks),
        "malformed_chunks": malformed,
        "total_chars": len(text),
        "completed_done": completed,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
