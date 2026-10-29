"""Plausible if/else bug: loses microphone when an app also declares camera."""

import json
import os
import runpy
from pathlib import Path

drill = Path(__file__).resolve().parents[1]
runpy.run_path(str(drill / "solutions" / "solve.py"))
report = Path(os.environ["OUT"]) / "report.json"
data = json.loads(report.read_text(encoding="utf-8"))
for app in data["apps"]:
    if app["id"] == "com.example.capture":
        app["permissions"] = ["camera"]
report.write_text(json.dumps(data) + "\n", encoding="utf-8")
