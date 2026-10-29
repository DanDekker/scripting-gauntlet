#!/usr/bin/env python3
"""074-jsonl-latest - one pass in input order, newest timestamp wins."""

import json
import os
from pathlib import Path

inp = Path(os.environ["IN"])
out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

best: dict[str, tuple[str, str]] = {}
records = 0

for lineno, raw in enumerate(
    (inp / "events.jsonl").read_text(encoding="utf-8").splitlines(), 1
):
    line = raw.strip()
    if not line:
        continue
    try:
        record = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"line {lineno}: bad JSON: {exc}")
    if not isinstance(record, dict):
        raise SystemExit(f"line {lineno}: not an object")
    rid, ts, status = record.get("id"), record.get("ts"), record.get("status")
    if not all(isinstance(value, str) for value in (rid, ts, status)):
        raise SystemExit(f"line {lineno}: id, ts and status must be strings")
    records += 1
    if rid not in best or ts >= best[rid][0]:
        best[rid] = (ts, status)

with (out / "latest.csv").open("w", newline="", encoding="utf-8") as fh:
    fh.write("id,ts,status\n")
    for rid in sorted(best):
        ts, status = best[rid]
        fh.write(f"{rid},{ts},{status}\n")

summary = {"records": records, "ids": len(best), "dropped": records - len(best)}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
