#!/usr/bin/env python3
"""Redact secrets, emails and card numbers out of captured tool output.

Three rules per line, in order: secret values, then email addresses, then card-like
runs. Each rule sees the line as the previous rule left it.
"""

import json
import os
import re
from pathlib import Path

KEYS = "api_key|apikey|secret|password|passwd|token|authorization|access_key"

SECRET = re.compile(
    rf"(?<![A-Za-z0-9_])(?P<key>{KEYS})(?P<sep>[ \t]*[=:][ \t]*)"
    rf"(?P<val>.*?)(?=(?:[ \t]+(?:{KEYS})[ \t]*[=:])|$)",
    re.IGNORECASE,
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+")
CARD = re.compile(r"(?<![0-9])[0-9](?:[ -]?[0-9]){12,18}(?![ -]?[0-9])")
PLACEHOLDERS = {"redacted", "****", "xxxxx", "null", "none"}


def sensitive(value):
    return len(value) >= 6 and value.lower() not in PLACEHOLDERS


def redact_secrets(line):
    """Replace sensitive values in place; keep key and separator exactly as written."""
    count = 0

    def swap(match):
        nonlocal count
        if not sensitive(match.group("val").rstrip(" \t")):
            return match.group(0)
        count += 1
        return match.group("key") + match.group("sep") + "[REDACTED]"

    return SECRET.sub(swap, line), count


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    text = (in_dir / "output.txt").read_text(encoding="utf-8")
    ends_nl = text.endswith("\n")
    if text == "":
        lines = []
    else:
        lines = text.split("\n")
        if ends_nl:
            lines.pop()

    out_lines = []
    summary = {"lines": 0, "secrets": 0, "emails": 0, "cards": 0, "changed": 0}
    for line in lines:
        redacted, secrets = redact_secrets(line)
        redacted, emails = EMAIL.subn("[EMAIL]", redacted)
        redacted, cards = CARD.subn("[CARD]", redacted)
        out_lines.append(redacted)
        summary["lines"] += 1
        summary["secrets"] += secrets
        summary["emails"] += emails
        summary["cards"] += cards
        if redacted != line:
            summary["changed"] += 1

    body = "\n".join(out_lines) + ("\n" if ends_nl else "")
    (out_dir / "redacted.txt").write_text(body, encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
