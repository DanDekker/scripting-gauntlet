#!/usr/bin/env python3
"""073-http-pagination - follow next, append everything, dedupe once."""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

out = Path(os.environ["OUT"])
base = os.environ["API_BASE"].rstrip("/")
out.mkdir(parents=True, exist_ok=True)

rows: list[tuple[int, str]] = []
cursor = ""
pages = 0
while True:
    pages += 1
    if pages > 10:
        raise SystemExit("pagination did not terminate after 10 pages")
    url = f"{base}/items" + (f"?cursor={cursor}" if cursor else "")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.status
            payload = response.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"HTTP {exc.code} from {url}")
    except OSError as exc:
        raise SystemExit(f"transport failure for {url}: {exc}")
    if status != 200:
        raise SystemExit(f"HTTP {status} from {url}")
    try:
        page = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"bad JSON from {url}: {exc}")
    items = page.get("items") if isinstance(page, dict) else None
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        raise SystemExit(f"items is not an array of objects in {url}")
    for item in items:
        if not isinstance(item.get("id"), int) or not isinstance(item.get("name"), str):
            raise SystemExit(f"item without int id / string name in {url}")
        rows.append((item["id"], item["name"]))
    next_cursor = page.get("next")
    if next_cursor is None:
        break
    if not isinstance(next_cursor, str) or not next_cursor:
        raise SystemExit(f"bad next cursor in {url}")
    cursor = next_cursor

seen: set[int] = set()
unique = []
for item_id, name in rows:
    if item_id in seen:
        continue
    seen.add(item_id)
    unique.append((item_id, name))
unique.sort(key=lambda row: row[0])

with (out / "items.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("id,name\n")
    for item_id, name in unique:
        fh.write(f"{item_id},{name}\n")

summary = {"pages": pages, "items": len(unique), "duplicates": len(rows) - len(unique)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
