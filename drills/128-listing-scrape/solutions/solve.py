#!/usr/bin/env python3
"""128-listing-scrape - saved listing page -> out/items.csv + out/summary.json."""

from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# Decode order matters: `&amp;` last, so `&amp;lt;` becomes `&lt;` and not `<`.
ENTITIES = (
    ("&#39;", "'"),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&quot;", '"'),
    ("&apos;", "'"),
    ("&amp;", "&"),
)

PRICE_RE = re.compile(r"\$([0-9,]+)(?:\.([0-9]{1,2}))?")
FIELDS = ("name", "price", "link")


def decode(text: str) -> str:
    for src, dst in ENTITIES:
        text = text.replace(src, dst)
    return text


def normalise(text: str) -> str:
    return " ".join(decode(text).split())


def price_cents(text: str) -> int | None:
    match = PRICE_RE.fullmatch(text.strip())
    if match is None:
        return None
    whole = match.group(1).replace(",", "")
    frac = (match.group(2) or "").ljust(2, "0")
    return int(whole) * 100 + int(frac)


def cents_str(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def cell(value: str) -> str:
    if any(ch in value for ch in ',"\n'):
        return '"' + value.replace('"', '""') + '"'
    return value


class Listing(HTMLParser):
    """Collect one record per `div.item`, innermost-item-owned."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.items: list[dict[str, str | None]] = []
        self.stack: list[dict] = []

    def _owner(self) -> int | None:
        for node in reversed(self.stack):
            if node["item"] is not None:
                return node["item"]
        return None

    def handle_starttag(self, tag, attrs) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        classes = values.get("class", "").split()
        node = {"tag": tag, "item": None, "field": None, "owner": None, "text": None}

        if tag == "div" and "item" in classes:
            self.items.append({field: None for field in FIELDS})
            node["item"] = len(self.items) - 1
        owner = node["item"] if node["item"] is not None else self._owner()

        if tag == "span" and len(classes) == 1 and classes[0] in ("name", "price"):
            field = classes[0]
            if owner is not None and self.items[owner][field] is None:
                self.items[owner][field] = ""  # claim now: the first element wins
                node["field"] = field
                node["owner"] = owner
                node["text"] = []
        elif tag == "a" and classes == ["link"]:
            if owner is not None and self.items[owner]["link"] is None:
                self.items[owner]["link"] = decode(values.get("href", "")).strip()

        self.stack.append(node)

    def _text(self, data: str) -> None:
        for node in reversed(self.stack):
            if node["field"] is not None:
                node["text"].append(data)
                return

    def handle_data(self, data) -> None:
        self._text(data)

    # convert_charrefs=False routes entities here instead of through handle_data; put
    # them back verbatim so ENTITIES stays the single source of truth for decoding.
    def handle_entityref(self, name) -> None:
        self._text(f"&{name};")

    def handle_charref(self, name) -> None:
        self._text(f"&#{name};")

    def handle_endtag(self, tag) -> None:
        while self.stack:
            node = self.stack.pop()
            if node["field"] is not None and node["text"]:
                self.items[node["owner"]][node["field"]] = normalise("".join(node["text"]))
            if node["tag"] == tag:
                break


def main() -> int:
    inp = Path(os.environ.get("IN", "in"))
    out = Path(os.environ.get("OUT", "out"))
    page = inp / "page.html"
    if not page.is_file():
        print(f"missing {page}", file=sys.stderr)
        return 1

    listing = Listing()
    listing.feed(page.read_text(encoding="utf-8"))
    listing.close()

    rows: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    skipped = duplicates = priced = 0
    total = 0

    for item in listing.items:
        name = item["name"] or ""
        if not name:
            skipped += 1
            continue
        cents = price_cents(item["price"] or "")
        price = "" if cents is None else cents_str(cents)
        key = (name, price)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        rows.append((name, price, (item["link"] or "").strip()))
        if cents is not None:
            priced += 1
            total += cents

    out.mkdir(parents=True, exist_ok=True)
    body = ["name,price,link"]
    body += [",".join(cell(value) for value in row) for row in rows]
    (out / "items.csv").write_text("\n".join(body) + "\n", encoding="utf-8")

    summary = (
        "{"
        f'"items":{len(listing.items)},'
        f'"kept":{len(rows)},'
        f'"skipped":{skipped},'
        f'"duplicates":{duplicates},'
        f'"priced":{priced},'
        f'"unpriced":{len(rows) - priced},'
        f'"total":{cents_str(total)}'
        "}\n"
    )
    (out / "summary.json").write_text(summary, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
