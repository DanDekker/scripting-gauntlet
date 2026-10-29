#!/usr/bin/env python3
"""Route each request to the best available tool; report unrouted honestly."""

import json
import os
import re
import sys
from pathlib import Path

WORD = re.compile(r"^[A-Za-z0-9_]+$")


def hits(text, keyword):
    """True when the keyword occurs in the text: whole word, or substring for odd keys."""
    if WORD.match(keyword):
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(keyword) + r"(?![A-Za-z0-9_])"
        return re.search(pattern, text, re.IGNORECASE) is not None
    return keyword.lower() in text.lower()


def load_tools(path):
    catalogue = json.loads(path.read_text(encoding="utf-8"))
    tools = []
    for tool in catalogue.get("tools") or []:
        name = tool.get("name")
        if not isinstance(name, str) or not name:
            continue
        keywords = [k for k in (tool.get("keywords") or []) if isinstance(k, str) and k]
        requires = [r for r in (tool.get("requires") or []) if isinstance(r, str)]
        tools.append({"name": name, "keywords": keywords, "requires": requires})
    return tools


def load_requests(path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if not isinstance(obj.get("id"), str) or not isinstance(obj.get("text"), str):
            continue
        context = obj.get("context")
        if not isinstance(context, list):
            context = []
        records.append({"id": obj["id"], "text": obj["text"], "context": context})
    return records


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    for name in ("tools.json", "requests.jsonl"):
        if not (in_dir / name).is_file():
            sys.exit(f"missing {in_dir / name}")
    out_dir.mkdir(parents=True, exist_ok=True)

    tools = load_tools(in_dir / "tools.json")
    records = load_requests(in_dir / "requests.jsonl")

    routes = []
    for record in records:
        candidates = []
        for tool in tools:
            score = sum(1 for keyword in tool["keywords"] if hits(record["text"], keyword))
            if score == 0:
                continue
            if any(need not in record["context"] for need in tool["requires"]):
                continue
            candidates.append((score, tool["name"]))
        if candidates:
            candidates.sort(key=lambda item: (-item[0], item[1]))
            routes.append((record["id"], candidates[0][1], candidates[0][0]))
        else:
            routes.append((record["id"], "", 0))

    lines = ["id,tool,matched"]
    for rid, tool, matched in routes:
        lines.append(f"{rid},{tool},{matched}")
    (out_dir / "routes.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    by_tool = {}
    for _, tool, _ in routes:
        if tool:
            by_tool[tool] = by_tool.get(tool, 0) + 1
    routed = sum(by_tool.values())
    summary = {
        "requests": len(routes),
        "routed": routed,
        "unrouted": len(routes) - routed,
        "by_tool": by_tool,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
