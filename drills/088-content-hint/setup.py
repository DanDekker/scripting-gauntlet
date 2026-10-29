#!/usr/bin/env python3
"""Add the oversized log that must be skipped rather than searched."""

import os
from pathlib import Path

notes = Path(os.environ["IN"]) / "notes"
(notes / "big.log").write_text("x" * 2 * 1024 * 1024, encoding="utf-8")
