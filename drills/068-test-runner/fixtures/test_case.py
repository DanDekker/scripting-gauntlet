#!/usr/bin/env python3
"""Deterministic smoke tests used by the portable test-runner drill."""

import json
import os
import sys
from pathlib import Path

name = sys.argv[1]
root = Path(os.environ["IN"])
try:
    if name == "unit":
        assert sum([2, 3, 5]) == 10
    elif name == "schema":
        records = json.loads((root / "users.json").read_text(encoding="utf-8"))
        assert len(records) == 2 and all({"id", "name", "active"} <= record.keys() for record in records)
    elif name == "config":
        settings = dict(
            line.split("=", 1)
            for line in (root / "app.ini").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        assert settings == {"mode": "production", "retries": "3"}
    else:
        raise ValueError(f"unknown test: {name}")
except Exception as exc:
    print(f"FAIL {name}: {str(exc).replace(',', ';')}", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS {name}")
