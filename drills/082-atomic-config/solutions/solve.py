#!/usr/bin/env python3
"""082-atomic-config - validate, stage beside the target, rename over it."""

import json
import os
import re
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
live = out / "live"
target = live / "app.conf"
live.mkdir(parents=True, exist_ok=True)

KEY = re.compile(r"^[a-z_][a-z0-9_]*=")


def first_bad(path: Path):
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not KEY.match(line):
            return lineno
    return None


def apply(candidate: Path) -> None:
    mode = target.stat().st_mode & 0o777
    temp = live / f".{target.name}.{os.getpid()}.tmp"
    temp.write_text(candidate.read_text(encoding="utf-8"), encoding="utf-8")
    temp.chmod(mode)
    os.replace(temp, target)


summary = {"applied": False, "rejected": False, "mode": ""}
for name in ("update.valid", "update.invalid"):
    candidate = inp / name
    line = first_bad(candidate)
    if line is not None:
        with (out / "reject.log").open("a", encoding="utf-8") as fh:
            fh.write(f"rejected {name}:{line}\n")
        summary["rejected"] = True
        continue
    apply(candidate)
    summary["applied"] = True

summary["mode"] = format(target.stat().st_mode & 0o777, "o")
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
