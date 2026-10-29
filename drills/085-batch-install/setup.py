#!/usr/bin/env python3
"""Seed out/target from the current config directory."""

import os
import shutil
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])

target = out / "target"
if target.exists():
    shutil.rmtree(target)
shutil.copytree(inp / "target", target)
