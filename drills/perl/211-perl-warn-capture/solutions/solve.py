#!/usr/bin/env python3
"""211-perl-warn-capture — python twin using the warnings module."""

import json
import os
import warnings
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

messages = []
for line in (IN / "warnings.txt").read_text(encoding="utf-8").splitlines():
    messages.append(line)

captured = []
with warnings.catch_warnings(record=True) as records:
    warnings.simplefilter("always")
    for message in messages:
        warnings.warn(message)
        captured.append(str(records[-1].message))

captured_before_final = len(captured)
warnings.warn("rotation complete")
final_captured = "true" if len(captured) > captured_before_final else "false"

with (OUT / "warnings.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("index,message\n")
    for index, message in enumerate(captured, start=1):
        fh.write(f"{index},{message}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "emitted": len(messages) + 1,
            "captured": len(captured),
            "final_captured": final_captured,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
