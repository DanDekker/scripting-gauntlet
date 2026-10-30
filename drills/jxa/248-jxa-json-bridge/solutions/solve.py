#!/usr/bin/env python3
"""248-jxa-json-bridge — portable reference."""

import json
import os
from pathlib import Path


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
source = json.loads((inp / "records.json").read_text(encoding="utf-8"))
records = []
null_owner = missing_owner = tagged = 0
for record in source:
    if "owner" not in record:
        owner_state, owner = "missing", ""
        missing_owner += 1
    elif record["owner"] is None:
        owner_state, owner = "null", ""
        null_owner += 1
    else:
        owner_state, owner = "value", str(record["owner"]).strip()
    tagged += bool(record["tags"])
    records.append(
        {
            "id": record["id"],
            "owner_state": owner_state,
            "owner": owner,
            "tags": record["tags"],
            "enabled": record["enabled"],
        }
    )

out.mkdir(parents=True, exist_ok=True)
(out / "report.json").write_text(
    json.dumps(
        {
            "records": records,
            "summary": {
                "records": len(records),
                "null_owner": null_owner,
                "missing_owner": missing_owner,
                "tagged": tagged,
            },
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
