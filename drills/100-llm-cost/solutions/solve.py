#!/usr/bin/env python3
"""Cost a JSONL request log against a per-1k rate table."""

import csv
import json
import os
from pathlib import Path

CACHE_FACTOR = 0.1
REQUIRED = ("request_id", "model", "input_tokens")
PRICING_HEADER = ["model", "input_per_1k", "output_per_1k"]


def money(value):
    return f"{value:.6f}"


def load_pricing(path):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = [[cell.strip() for cell in row] for row in csv.reader(fh)]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows or rows[0] != PRICING_HEADER:
        raise SystemExit(f"{path}: expected header {PRICING_HEADER!r}, got {rows[:1]!r}")
    table = {}
    for row in rows[1:]:
        if len(row) < 3:
            raise SystemExit(f"{path}: short pricing row {row!r}")
        table[row[0]] = (float(row[1]), float(row[2]))
    return table


def load_records(path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if any(field not in obj for field in REQUIRED):
            continue
        records.append(obj)
    return records


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    pricing = load_pricing(in_dir / "pricing.csv")
    records = load_records(in_dir / "usage.jsonl")

    rows = []
    by_model = {}
    unpriced = 0
    total = 0.0
    for record in records:
        model = str(record["model"])
        if model not in pricing:
            unpriced += 1
            continue
        input_rate, output_rate = pricing[model]
        if record.get("cached") is True:
            input_rate *= CACHE_FACTOR
        tokens_in = float(record["input_tokens"])
        tokens_out = float(record.get("output_tokens") or 0)
        cost = round(tokens_in / 1000 * input_rate + tokens_out / 1000 * output_rate, 6)
        rows.append((str(record["request_id"]), model, cost))
        by_model[model] = by_model.get(model, 0.0) + cost
        total += cost

    rows.sort(key=lambda row: (row[0], row[1]))

    with (out_dir / "costs.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["request_id", "model", "cost"])
        for request_id, model, cost in rows:
            writer.writerow([request_id, model, money(cost)])

    models = sorted(by_model)
    lines = [
        "{",
        f'  "requests": {len(records)},',
        f'  "priced": {len(rows)},',
        f'  "unpriced": {unpriced},',
        f'  "total_cost": {money(round(total, 6))},',
        '  "by_model": {',
    ]
    for index, model in enumerate(models):
        comma = "," if index < len(models) - 1 else ""
        lines.append(f"    {json.dumps(model)}: {money(by_model[model])}{comma}")
    lines.append("  }")
    lines.append("}")
    (out_dir / "summary.json").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
