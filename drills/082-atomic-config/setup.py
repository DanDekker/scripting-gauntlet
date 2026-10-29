#!/usr/bin/env python3
"""Stage the live config with the right mode, so the drill starts from a real 0640 file."""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])

live = out / "live"
live.mkdir(parents=True, exist_ok=True)
target = live / "app.conf"
target.write_text((inp / "app.conf").read_text(encoding="utf-8"), encoding="utf-8")
target.chmod(0o640)
