#!/usr/bin/env python3
"""Audit agent tool invocations against a capability security policy."""

import csv
import json
import os
from pathlib import Path


def host_of(url):
    """Host of a URL: after ://, before /, after the last @, before the first :."""
    if "://" not in url:
        return ""
    rest = url.split("://", 1)[1].split("/", 1)[0]
    rest = rest.rsplit("@", 1)[-1]
    return rest.split(":", 1)[0].lower()


def load_invocations(path):
    invocations = []
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
        ident = record.get("id")
        if not isinstance(ident, str) or ident == "":
            continue
        tool = record.get("tool")
        args = record.get("args")
        invocations.append(
            {
                "id": ident,
                "tool": tool if isinstance(tool, str) else "",
                "args": args if isinstance(args, dict) else {},
            }
        )
    return invocations


def violations_of(invocation, policy):
    tool = invocation["tool"]
    args = invocation["args"]
    found = []

    cmd = args.get("cmd")
    if tool == "bash" and isinstance(cmd, str):
        if any(banned in cmd for banned in policy.get("banned_commands", [])):
            found.append("banned-command")

    if tool == "http_get":
        url = args.get("url")
        if host_of(url if isinstance(url, str) else "") not in policy.get("allowed_domains", []):
            found.append("disallowed-domain")

    path = args.get("path")
    if isinstance(path, str):
        if path.startswith("/") or ".." in path.split("/"):
            found.append("path-traversal")

    if tool not in policy.get("allowed_tools", []):
        found.append("unknown-tool")

    found.sort()
    return found


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    policy = json.loads((in_dir / "policy.json").read_text(encoding="utf-8"))
    invocations = load_invocations(in_dir / "trace.jsonl")

    rows = []
    violations_count = 0
    for invocation in invocations:
        found = violations_of(invocation, policy)
        violations_count += len(found)
        rows.append(
            {
                "id": invocation["id"],
                "tool": invocation["tool"],
                "verdict": "allowed" if not found else "denied",
                "violations": ";".join(found),
            }
        )
    rows.sort(key=lambda row: row["id"])

    with (out_dir / "audit.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["id", "tool", "verdict", "violations"])
        for row in rows:
            writer.writerow([row["id"], row["tool"], row["verdict"], row["violations"]])

    allowed = sum(1 for row in rows if row["verdict"] == "allowed")
    summary = {
        "total_invocations": len(rows),
        "allowed_count": allowed,
        "denied_count": len(rows) - allowed,
        "violations_count": violations_count,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
