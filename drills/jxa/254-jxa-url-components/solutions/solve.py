#!/usr/bin/env python3
"""254-jxa-url-components — portable reference."""

import csv
import json
import os
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit


inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
rows = []
skipped = 0
query_params = 0
with (inp / "urls.csv").open(newline="", encoding="utf-8") as fh:
    for source in csv.DictReader(fh):
        raw = source["url"].strip()
        parsed = urlsplit(raw)
        if not parsed.scheme or (not parsed.hostname and parsed.scheme != "file"):
            skipped += 1
            continue
        count = len(parse_qsl(parsed.query, keep_blank_values=True))
        query_params += count
        rows.append(
            (
                source["id"].strip(),
                parsed.scheme,
                parsed.hostname or "",
                parsed.port or "",
                unquote(parsed.path),
                count,
            )
        )

out.mkdir(parents=True, exist_ok=True)
with (out / "urls.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow(["id", "scheme", "host", "port", "path", "query_items"])
    writer.writerows(rows)
(out / "summary.json").write_text(
    json.dumps({"urls": len(rows), "skipped": skipped, "query_params": query_params}, separators=(",", ":"))
    + "\n",
    encoding="utf-8",
)
