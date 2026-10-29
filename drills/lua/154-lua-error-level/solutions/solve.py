#!/usr/bin/env python3
"""154-lua-error-level — same contract, the reason text is raised and caught unchanged."""

import json
import os
import re
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
VALUE_RE = re.compile(r"^\d+$")


def csv_field(value: str) -> str:
    if any(ch in value for ch in ',"\r\n'):
        return '"' + value.replace('"', '""') + '"'
    return value


class DirectiveError(Exception):
    """The reason text is the message, with no prefix added."""


def check(line: str) -> tuple[str, str]:
    if "=" not in line:
        raise DirectiveError("missing '='")
    key, _, value = line.partition("=")
    key = key.strip()
    value = value.strip()
    if not key or not KEY_RE.match(key):
        raise DirectiveError(f"bad key: {key}")
    if not VALUE_RE.match(value):
        raise DirectiveError(f"not an integer: {value}")
    return key, value


errors: list[tuple[int, str]] = []
accepted: list[tuple[str, str]] = []
seen: set[str] = set()
lines = 0

for raw in (IN / "records.txt").read_text(encoding="utf-8").splitlines():
    lines += 1
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    try:
        key, value = check(line)
    except DirectiveError as exc:
        errors.append((lines, str(exc)))
        continue
    if key in seen:
        errors.append((lines, f"duplicate key: {key}"))
        continue
    seen.add(key)
    accepted.append((key, value))

with (OUT / "errors.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("line,reason\n")
    for number, reason in errors:
        fh.write(f"{number},{csv_field(reason)}\n")

with (OUT / "accepted.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("key,value\n")
    for key, value in accepted:
        fh.write(f"{key},{csv_field(value)}\n")

(OUT / "summary.json").write_text(
    json.dumps({"lines": lines, "accepted": len(accepted), "errors": len(errors)}) + "\n",
    encoding="utf-8",
)
