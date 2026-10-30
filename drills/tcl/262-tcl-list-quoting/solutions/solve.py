#!/usr/bin/env python3
"""262-tcl-list-quoting — portable reference."""

import csv
import json
import os
import re
from pathlib import Path


def split_tcl_list(text):
    words = []
    for match in re.finditer(r"\{([^{}]*)\}|\"([^\"]*)\"|(\S+)", text):
        words.append(next(group for group in match.groups() if group is not None))
    return words


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
with_spaces = 0
for raw in (inp / "commands.txt").read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    words = split_tcl_list(raw)
    target = words[1]
    with_spaces += " " in target
    rows.append((words[0], target, len(words) - 1))

out.mkdir(parents=True, exist_ok=True)
with (out / "commands.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["command", "target", "args"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"commands": len(rows), "with_spaces": with_spaces}, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
