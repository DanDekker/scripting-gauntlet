#!/usr/bin/env python3
"""259-tcl-safe-subst — portable reference."""

import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
values = {}
for raw in (inp / "values.tsv").read_text(encoding="utf-8").splitlines():
    key, value = raw.split("\t", 1)
    values[key] = value.strip()
template = (inp / "template.txt").read_text(encoding="utf-8")
for key, value in values.items():
    template = template.replace("$" + key, value)
out.mkdir(parents=True, exist_ok=True)
(out / "rendered.txt").write_text(template, encoding="utf-8")
