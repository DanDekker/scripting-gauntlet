#!/usr/bin/env python3
"""Write the handoff note: what was asked, what was touched, what is still broken."""

import json
import os
from pathlib import Path


def merge(lines):
    """Fold indented continuation lines into the previous non-continuation line."""
    merged = []
    for raw in lines:
        if raw[:1] in (" ", "\t"):
            text = raw.strip()
            if not merged or not text:
                continue
            merged[-1] = merged[-1] + " " + text
            continue
        merged.append(raw)
    return merged


def parse(lines):
    request = ""
    tools = []
    call_names = []
    result_names = set()
    notes = []
    errors = []

    for raw in merge(lines):
        text = raw.strip()
        head = text.split(None, 1)
        keyword = head[0] if head else ""
        rest = head[1] if len(head) == 2 else ""

        if text.startswith("USER:"):
            request = text[len("USER:"):].strip()
        elif keyword == "TOOL" and rest.split():
            name = rest.split()[0]
            call_names.append(name)
            if name not in tools:
                tools.append(name)
        elif keyword == "RESULT" and ":" in rest:
            result_names.add(rest.split(":", 1)[0].strip())
        elif text.startswith("NOTE:"):
            notes.append(text[len("NOTE:"):].strip())
        elif text.startswith("ERROR:"):
            errors.append(text[len("ERROR:"):].strip())

    handoff = {
        "request": request,
        "tools": tools,
        "results": len(result_names),
        "notes": notes,
        "errors": errors,
        "calls": len(call_names),
        "unresolved": sum(1 for name in call_names if name not in result_names),
    }
    return handoff


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = (in_dir / "session.log").read_text(encoding="utf-8").splitlines()
    handoff = parse(lines)
    (out_dir / "handoff.json").write_text(json.dumps(handoff, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
