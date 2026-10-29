#!/usr/bin/env python3
"""129-crawl-frontier - breadth-first crawl of a saved link graph."""

from __future__ import annotations

import json
import os
import re
import sys
from collections import deque
from pathlib import Path

ABSOLUTE = re.compile(r"https?://\S+")
HREF = re.compile(r'href\s*=\s*"([^"]*)"')


def normalise(url: str) -> str:
    """Page identity: surrounding whitespace and the #fragment are not part of it."""
    return url.strip().split("#", 1)[0]


def host_of(url: str) -> str:
    rest = url.split("://", 1)[1]
    return rest.split("/", 1)[0]


def absolute(url: str) -> bool:
    return bool(ABSOLUTE.fullmatch(url))


def parse_sitemap(path: Path) -> tuple[list[str], dict[str, list[str]]]:
    """Return (pages in first-seen order, page -> link list in document order)."""
    order: list[str] = []
    links: dict[str, list[str]] = {}
    owner: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("<"):
            match = HREF.search(line)
            if match is None or owner is None:
                continue
            target = normalise(match.group(1))
            if absolute(target) and target != owner:
                links[owner].append(target)
            continue
        if absolute(line):
            page = normalise(line)
            if page not in links:  # a repeated page line merges into the first one
                order.append(page)
                links[page] = []
            owner = page
        # any other line is noise: ignored, and it does not change ownership
    return order, links


def crawl(
    seed: str, links: dict[str, list[str]], max_depth: int, same_host: str, limit: int
) -> tuple[list[tuple[str, int]], int, bool]:
    """Return (visited pages with depth in visit order, skipped count, limit_reached)."""
    if seed not in links:
        return [], 0, False

    visited: dict[str, int] = {}
    order: list[tuple[str, int]] = []
    discovered = {seed}
    frontier: deque[tuple[str, int]] = deque([(seed, 0)])
    skipped = 0

    while frontier and len(visited) < limit:
        url, depth = frontier.popleft()
        visited[url] = depth
        order.append((url, depth))
        if depth >= max_depth:
            continue  # a page at the depth limit contributes no new links
        for target in links.get(url, []):
            if target not in links or target in discovered or target in visited:
                skipped += 1
            elif same_host and host_of(target) != same_host:
                skipped += 1
            else:
                discovered.add(target)
                frontier.append((target, depth + 1))

    return order, skipped, len(visited) == limit and bool(frontier)


def main() -> int:
    inp = Path(os.environ.get("IN", "in"))
    out = Path(os.environ.get("OUT", "out"))
    for name in ("sitemap.txt", "config.json"):
        if not (inp / name).is_file():
            print(f"missing {inp / name}", file=sys.stderr)
            return 1

    config = json.loads((inp / "config.json").read_text(encoding="utf-8"))
    seed = normalise(config["seed"])
    max_depth = int(config["max_depth"])
    same_host = (config.get("same_host") or "").strip()
    limit = int(config["limit"])

    pages, links = parse_sitemap(inp / "sitemap.txt")
    order, skipped, limit_reached = crawl(seed, links, max_depth, same_host, limit)

    # inbound is a property of the whole site graph, not of the visited subset.
    inbound: dict[str, int] = {}
    counted: set[tuple[str, str]] = set()
    for source in pages:
        for target in links[source]:
            if target not in links or (target, source) in counted:
                continue
            counted.add((target, source))
            inbound[target] = inbound.get(target, 0) + 1

    out.mkdir(parents=True, exist_ok=True)
    body = ["url,depth,inbound"]
    body += [f"{url},{depth},{inbound.get(url, 0)}" for url, depth in order]
    (out / "pages.csv").write_text("\n".join(body) + "\n", encoding="utf-8")

    summary = (
        "{"
        f'"visited":{len(order)},'
        f'"skipped":{skipped},'
        f'"limit_reached":{"true" if limit_reached else "false"},'
        f'"max_depth_reached":{max((d for _, d in order), default=0)},'
        f'"orphan":{len(pages) - len(order)}'
        "}\n"
    )
    (out / "summary.json").write_text(summary, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
