#!/usr/bin/env python3
"""004-scrape-table — html.parser, scoped to the #pricing table."""

import os
from html.parser import HTMLParser
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)


class PricingTable(HTMLParser):
    """Collects only the cells of <table id="pricing">."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_table = False
        self.depth = 0
        self.in_badge = 0
        self.cell = None
        self.row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            if self.in_table:
                self.depth += 1
            elif attrs.get("id") == "pricing":
                self.in_table = True
                self.depth = 1
            return
        if not self.in_table:
            return
        if tag == "tr":
            self.row = []
        elif tag == "td":
            self.cell = []
        elif tag == "span" and "badge" in (attrs.get("class") or ""):
            self.in_badge += 1

    def handle_endtag(self, tag):
        if not self.in_table:
            return
        if tag == "td" and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = []
        elif tag == "span" and self.in_badge:
            self.in_badge -= 1
        elif tag == "table":
            self.depth -= 1
            if self.depth == 0:
                self.in_table = False

    def handle_data(self, data):
        if self.in_table and self.cell is not None and not self.in_badge:
            self.cell.append(data)


parser = PricingTable()
parser.feed((inp / "pricing.html").read_text(encoding="utf-8"))

plans = []
for row in parser.rows:
    if len(row) < 3:
        continue
    name, seats, price = row[0], row[1], row[2]
    try:
        seat_count = int(seats)
        monthly = float(price.replace("$", "").replace(",", ""))
    except ValueError:
        continue
    if name:
        plans.append((name, seat_count, monthly))

plans.sort(key=lambda plan: (-plan[2], plan[0]))

with (out / "pricing.csv").open("w", encoding="utf-8", newline="") as fh:
    fh.write("plan,seats,monthly_usd\n")
    for name, seats, monthly in plans:
        fh.write(f"{name},{seats},{monthly:.2f}\n")
