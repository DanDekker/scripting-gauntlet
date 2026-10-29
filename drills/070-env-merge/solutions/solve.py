#!/usr/bin/env python3
"""070-env-merge - last file wins; quotes and comments are syntax, not data."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FILES = ["base.env", "local.env"]

values: dict[str, str] = {}
sources: dict[str, set[str]] = {}

for name in FILES:
    path = inp / name
    if not path.is_file():
        raise SystemExit(f"missing {path}")
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            raise SystemExit(f"{name}:{lineno}: no =")
        key, value = line.split("=", 1)
        key = key.strip()
        if not KEY.match(key):
            raise SystemExit(f"{name}:{lineno}: bad key {key!r}")
        value = value.strip()
        if value[:1] in ('"', "'"):
            quote = value[0]
            end = value.find(quote, 1)
            if end < 0:
                raise SystemExit(f"{name}:{lineno}: unterminated quote")
            value = value[1:end]
        else:
            hash_at = value.find("#")
            if hash_at >= 0:
                value = value[:hash_at].strip()
        values[key] = value
        sources.setdefault(key, set()).add(name)

config = {key: values[key] for key in sorted(values)}
(out / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

summary = {
    "files": len(FILES),
    "keys": len(values),
    "overridden": sum(1 for seen in sources.values() if len(seen) > 1),
    "empty": sum(1 for value in values.values() if value == ""),
}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
