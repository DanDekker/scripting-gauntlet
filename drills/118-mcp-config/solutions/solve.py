#!/usr/bin/env python3
"""Audit an MCP server config before an agent is allowed to launch it."""

import json
import os
import re
from pathlib import Path

IDENT = re.compile(r"^[a-z0-9_-]+$")
ALLOWED = ("command", "args", "env")


class Pairs(dict):
    """A dict that remembers which of its keys it saw more than once."""

    dups = ()


def hook(pairs):
    obj = Pairs()
    dups = []
    for key, value in pairs:
        if key in obj:
            dups.append(key)
        obj[key] = value
    obj.dups = tuple(dups)
    return obj


def audit(name, server, dup_names, env_names):
    """Every problem for one server, in contract order."""
    problems = []
    if name in dup_names:
        problems.append(("duplicate-name", "duplicate"))
    if not IDENT.match(name):
        problems.append(("bad-name", ""))
    command = server.get("command")
    if not isinstance(command, str):
        problems.append(("missing-command", ""))
    elif command.strip() == "":
        problems.append(("empty-command", ""))
    if "args" in server:
        args = server["args"]
        if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            problems.append(("bad-args", ""))
    env = server.get("env")
    if isinstance(env, dict):
        for var in env:
            if var not in env_names:
                problems.append(("undefined-env", var))
    for key in server:
        if key not in ALLOWED:
            problems.append(("unknown-key", key))
    return problems


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(
        (in_dir / "mcp.json").read_text(encoding="utf-8"), object_pairs_hook=hook
    )
    servers = config.get("servers")
    if not isinstance(servers, dict):
        servers = Pairs()
    dup_names = set(getattr(servers, "dups", ()))
    env_names = set(json.loads((in_dir / "env.json").read_text(encoding="utf-8")))

    rows = []
    valid = invalid = 0
    for name in sorted(servers):
        server = servers[name]
        if not isinstance(server, dict):
            server = {}
        problems = audit(name, server, dup_names, env_names)
        if problems:
            invalid += 1
        else:
            valid += 1
        for problem, detail in problems:
            rows.append((name, problem, detail))

    lines = ["server,problem,detail"] + [
        f"{name},{problem},{detail}" for name, problem, detail in rows
    ]
    (out_dir / "problems.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "servers": len(servers),
        "valid": valid,
        "invalid": invalid,
        "problems": len(rows),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
