#!/usr/bin/env python3
"""194-ruby-keyword-arguments — python twin with kwargs dispatch."""

import json
import os
from pathlib import Path

IN = Path(os.environ["IN"])
OUT = Path(os.environ["OUT"])

records = json.loads((IN / "endpoints.json").read_text(encoding="utf-8"))


def build_endpoint(host, port=8080, path="/", timeout=30):
    p = "" if path is None else path
    url = f"http://{host}:{port}{p}"
    t = "" if timeout is None else str(timeout)
    return url, t


rows = []
valid_count = 0
missing_host_count = 0
null_overrides_count = 0

for r in records:
    rid = r["id"]
    kwargs = {k: v for k, v in r.items() if k != "id"}

    if (
        "path" in kwargs
        and kwargs["path"] is None
        or "timeout" in kwargs
        and kwargs["timeout"] is None
    ):
        null_overrides_count += 1

    if "host" not in kwargs:
        rows.append((rid, "missing_host", "", ""))
        missing_host_count += 1
    else:
        url, t = build_endpoint(**kwargs)
        rows.append((rid, "valid", url, t))
        valid_count += 1

with (OUT / "endpoints.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("id,status,url,timeout\n")
    for r in rows:
        fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

(OUT / "summary.json").write_text(
    json.dumps(
        {
            "endpoints": len(rows),
            "valid": valid_count,
            "missing_host": missing_host_count,
            "null_overrides": null_overrides_count,
        },
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
