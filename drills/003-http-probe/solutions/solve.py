#!/usr/bin/env python3
"""003-http-probe — urllib and json, no dependencies."""

import json
import os
from pathlib import Path
from urllib.request import urlopen

base = os.environ.get("API_BASE")
if not base:
    raise SystemExit("API_BASE not set")
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


def get(path: str) -> dict:
    with urlopen(base + path, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


health = get("/health")
if health.get("ok") is not True:
    raise SystemExit(f"service reports unhealthy: {health}")

items: list[dict] = []
visited: set[str] = set()
pages = 0
next_path = "/api/v1/items?page=1"

while next_path:
    if next_path in visited:
        raise SystemExit(f"pagination loop at {next_path}")
    visited.add(next_path)
    pages += 1
    if pages > 50:
        raise SystemExit("exceeded 50 pages")

    page = get(next_path)
    items.extend(page["items"])
    next_path = page.get("next")

items.sort(key=lambda item: item["id"])

(out / "items.json").write_text(json.dumps(items) + "\n", encoding="utf-8")
report = {
    "ok": True,
    "version": health["version"],
    "item_count": len(items),
    "pages": pages,
}
(out / "report.json").write_text(json.dumps(report) + "\n", encoding="utf-8")
