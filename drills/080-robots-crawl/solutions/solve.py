#!/usr/bin/env python3
"""080-robots-crawl - pick one group, longest pattern wins."""

import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

AGENT = "scriptbot"


def to_regex(pattern: str) -> re.Pattern:
    parts = ["^"]
    for index, char in enumerate(pattern):
        if char == "*":
            parts.append(".*")
        elif char == "$" and index == len(pattern) - 1:
            parts.append("$")
        elif char in "\\.^$+?()[]{}|":
            parts.append("\\" + char)
        else:
            parts.append(char)
    return re.compile("".join(parts))


groups: dict[str, list[tuple[bool, str]]] = {}
agents: list[str] = []
in_rules = False
for raw in (inp / "robots.txt").read_text(encoding="utf-8").splitlines():
    line = raw.split("#", 1)[0].strip()
    if not line:
        agents, in_rules = [], False
        continue
    key, _, value = line.partition(":")
    key, value = key.strip().lower(), value.strip()
    if key == "user-agent":
        if in_rules:
            agents, in_rules = [], False
        agents.append(value.lower())
        groups.setdefault(value.lower(), [])
    elif key in ("allow", "disallow"):
        in_rules = True
        for agent in agents:
            groups.setdefault(agent, []).append((key == "allow", value))

rules = groups.get(AGENT) or groups.get("*", [])
compiled = [(allowed, pattern, to_regex(pattern)) for allowed, pattern in rules if pattern]

rows = []
for raw in (inp / "urls.txt").read_text(encoding="utf-8").splitlines():
    url = raw.strip()
    if not url or url.startswith("#"):
        continue
    split = urlsplit(url)
    target = split.path or "/"
    if split.query:
        target += "?" + split.query

    best_length = -1
    best_allow = True
    best_rule = ""
    for allowed, pattern, regex in compiled:
        if not regex.match(target):
            continue
        if len(pattern) > best_length or (len(pattern) == best_length and allowed):
            best_length, best_allow, best_rule = len(pattern), allowed, pattern
    rows.append((url, "yes" if best_allow else "no", best_rule))

rows.sort()
with (out / "crawl.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("url,allowed,rule\n")
    for url, allowed, rule in rows:
        fh.write(f"{url},{allowed},{rule}\n")

summary = {
    "urls": len(rows),
    "allowed": sum(1 for row in rows if row[1] == "yes"),
    "disallowed": sum(1 for row in rows if row[1] == "no"),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
