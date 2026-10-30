#!/usr/bin/env python3
"""252-jxa-plist-write — portable reference."""

import json
import os
import plistlib
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
data = json.loads((inp / "settings.json").read_text(encoding="utf-8"))
out.mkdir(parents=True, exist_ok=True)
with (out / "report.plist").open("wb") as fh:
    plistlib.dump(data, fh, fmt=plistlib.FMT_XML, sort_keys=False)
