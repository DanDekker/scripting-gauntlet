#!/usr/bin/env python3
"""Fold observations into a memory store: expire, resolve, then evict to capacity."""

import csv
import json
import os
from pathlib import Path


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def load(path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        key = obj.get("key")
        if not isinstance(key, str) or not key:
            continue
        ts = obj.get("ts")
        raw_value = obj.get("value")
        records.append(
            {
                "key": key,
                "value": "" if raw_value is None else str(raw_value),
                "ts": ts if is_number(ts) else 0,
                "ttl": obj.get("ttl") if is_number(obj.get("ttl")) else None,
            }
        )
    return records


def ts_text(ts) -> str:
    return str(int(ts)) if float(ts).is_integer() else str(ts)


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads((in_dir / "config.json").read_text(encoding="utf-8"))
    max_entries = int(config["max_entries"])
    as_of = config["as_of"]

    records = load(in_dir / "memory.jsonl")

    alive = []
    expired = 0
    for record in records:
        ttl = record["ttl"]
        if ttl is not None and ttl >= 0 and record["ts"] + ttl <= as_of:
            expired += 1
            continue
        alive.append(record)

    best = {}
    conflicts = 0
    for record in alive:  # input order, so a later line wins a ts tie
        current = best.get(record["key"])
        if current is None:
            best[record["key"]] = record
            continue
        conflicts += 1
        if record["ts"] >= current["ts"]:
            best[record["key"]] = record

    store = list(best.values())
    evicted = 0
    while len(store) > max_entries:
        oldest = min(record["ts"] for record in store)
        tied = [record for record in store if record["ts"] == oldest]
        store.remove(max(tied, key=lambda record: record["key"]))
        evicted += 1

    store.sort(key=lambda record: (-record["ts"], record["key"]))
    with (out_dir / "memory.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["key", "value", "ts"])
        for record in store:
            writer.writerow([record["key"], record["value"], ts_text(record["ts"])])

    summary = {
        "observations": len(records),
        "expired": expired,
        "conflicts": conflicts,
        "stored": len(store),
        "evicted": evicted,
        "keys": sorted(record["key"] for record in store),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
