#!/usr/bin/env python3
"""241-ps1-json-presence — portable reference."""

import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
records = json.loads((inp / "records.json").read_text(encoding="utf-8"))

rows = []
summary = {
    "records": len(records),
    "owner_missing": 0,
    "owner_null": 0,
    "owner_empty": 0,
    "quota_missing": 0,
    "quota_null": 0,
}

for record in records:
    if "owner" not in record:
        owner_state, owner_value = "missing", ""
        summary["owner_missing"] += 1
    elif record["owner"] is None:
        owner_state, owner_value = "null", ""
        summary["owner_null"] += 1
    elif isinstance(record["owner"], str) and not record["owner"].strip():
        owner_state, owner_value = "empty", ""
        summary["owner_empty"] += 1
    else:
        owner_state = "value"
        owner_value = record["owner"].strip() if isinstance(record["owner"], str) else str(record["owner"])

    if "quota" not in record:
        quota_state, quota_value = "missing", ""
        summary["quota_missing"] += 1
    elif record["quota"] is None:
        quota_state, quota_value = "null", ""
        summary["quota_null"] += 1
    else:
        quota_value = int(record["quota"])
        quota_state = "zero" if quota_value == 0 else "positive" if quota_value > 0 else "negative"

    rows.append((record["id"].strip(), owner_state, owner_value, quota_state, quota_value))

out.mkdir(parents=True, exist_ok=True)
with (out / "report.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,owner_state,owner_value,quota_state,quota_value\n")
    for row in rows:
        fh.write(",".join(str(cell) for cell in row) + "\n")
(out / "summary.json").write_text(json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8")
