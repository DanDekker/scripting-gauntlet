#!/usr/bin/env python3
"""Fill a {{template}} from a JSON bag of values and report the holes."""

import json
import os
import re
from pathlib import Path

# {{ name }} | {{name|default}} — the name is the part before the first '|'.
PLACEHOLDER = re.compile(r"\{\{[ \t]*([A-Za-z0-9_.-]+)[ \t]*(?:\|([^}]*))?\}\}")


def render_value(value):
    """Strings verbatim; everything else as JSON text (compact for arrays/objects)."""
    if isinstance(value, str):
        return value
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    values = json.loads((in_dir / "values.json").read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise SystemExit("values.json must be a JSON object")
    template = (in_dir / "template.txt").read_text(encoding="utf-8")

    stats = {"placeholders": 0, "holes": 0, "defaults_used": 0}
    names = set()

    def substitute(match):
        name = match.group(1)
        default = match.group(2)
        stats["placeholders"] += 1
        names.add(name)
        if name in values:
            return render_value(values[name])
        if default is not None:
            stats["defaults_used"] += 1
            return default.strip()
        stats["holes"] += 1
        return f"[MISSING:{name}]"

    lines = template.split("\n")
    rendered = "\n".join(PLACEHOLDER.sub(substitute, line) for line in lines)
    (out_dir / "rendered.txt").write_text(rendered, encoding="utf-8")

    summary = {
        "placeholders": stats["placeholders"],
        "distinct": len(names),
        "holes": stats["holes"],
        "unused": sorted(key for key in values if key not in names),
        "defaults_used": stats["defaults_used"],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
