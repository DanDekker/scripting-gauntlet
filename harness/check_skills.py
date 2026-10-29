#!/usr/bin/env python3
"""Validate skills/ against the Agent Skills spec.

Checks only what a client will actually choke on: a missing SKILL.md, bad frontmatter,
a name that does not match its directory, a missing or oversized description, and a body
too long to load comfortably.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_SKILL_LINES = 500


def parse_frontmatter(text: str) -> tuple[dict[str, str], int] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        value = value.strip().strip('"').strip("'")
        fields[key.strip()] = value
    return fields, end + 1


def check(skill_dir: Path) -> list[str]:
    problems: list[str] = []
    doc = skill_dir / "SKILL.md"
    if not doc.is_file():
        return [f"{skill_dir.name}: missing SKILL.md"]

    text = doc.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if parsed is None:
        return [f"{skill_dir.name}: SKILL.md has no --- delimited frontmatter"]
    fields, body_start = parsed

    name = fields.get("name", "")
    if not name:
        problems.append(f"{skill_dir.name}: missing required field 'name'")
    else:
        if len(name) > 64:
            problems.append(f"{skill_dir.name}: name is {len(name)} chars (max 64)")
        if not NAME_RE.match(name):
            problems.append(f"{skill_dir.name}: name {name!r} must be lowercase alphanumeric with single hyphens")
        if name != skill_dir.name:
            problems.append(f"{skill_dir.name}: name {name!r} must match the directory name")

    description = fields.get("description", "")
    if not description:
        problems.append(f"{skill_dir.name}: missing required field 'description'")
    elif len(description) > 1024:
        problems.append(f"{skill_dir.name}: description is {len(description)} chars (max 1024)")

    body_lines = len(text.splitlines()) - body_start
    if body_lines > MAX_SKILL_LINES:
        problems.append(
            f"{skill_dir.name}: body is {body_lines} lines (keep SKILL.md under {MAX_SKILL_LINES}; move detail to references/)"
        )

    return problems


def main() -> int:
    if not ROOT.is_dir():
        print(f"no skills/ directory at {ROOT}", file=sys.stderr)
        return 1

    dirs = sorted(d for d in ROOT.iterdir() if d.is_dir() and not d.name.startswith("."))
    if not dirs:
        print("no skills found", file=sys.stderr)
        return 1

    failures: list[str] = []
    for skill_dir in dirs:
        problems = check(skill_dir)
        failures.extend(problems)
        print(f"{'FAIL' if problems else 'ok  '}  {skill_dir.name}")
        for problem in problems:
            print(f"      - {problem}")

    print(f"\n{len(dirs) - len({f.split(':')[0] for f in failures})}/{len(dirs)} skills valid")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
