#!/usr/bin/env python3
"""Simulate two rate-limit buckets (requests, tokens) over a request log."""

import csv
import json
import os
import re
from pathlib import Path

INT_RE = re.compile(r"-?[0-9]+")


def load_config(path):
    cfg = json.loads(path.read_text(encoding="utf-8"))
    return (
        float(cfg["rpm_capacity"]),
        float(cfg["rpm_refill_per_sec"]),
        float(cfg["tpm_capacity"]),
        float(cfg["tpm_refill_per_sec"]),
    )


def load_requests(path):
    """Valid requests as (timestamp, line_number, id, tokens), already in order."""
    rows = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)  # header
        for lineno, raw in enumerate(reader, start=2):
            cells = [cell.strip() for cell in raw]
            if not any(cells) or len(cells) != 3:
                continue
            rid, ts_raw, tok_raw = cells
            if not rid or not INT_RE.fullmatch(ts_raw) or not INT_RE.fullmatch(tok_raw):
                continue
            tokens = int(tok_raw)
            if tokens < 0:
                continue
            rows.append((int(ts_raw), lineno, rid, tokens))
    rows.sort(key=lambda row: (row[0], row[1]))
    return rows


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    rpm_cap, rpm_rate, tpm_cap, tpm_rate = load_config(in_dir / "config.json")
    requests = load_requests(in_dir / "requests.csv")

    req_tokens = rpm_cap
    tok_tokens = tpm_cap
    prev_t = None
    decisions = []

    for ts, _, rid, need in requests:
        dt = 0 if prev_t is None else ts - prev_t
        req_tokens = min(rpm_cap, req_tokens + dt * rpm_rate)
        tok_tokens = min(tpm_cap, tok_tokens + dt * tpm_rate)

        if req_tokens >= 1.0 and tok_tokens >= need:
            status = "accept"
            req_tokens -= 1.0
            tok_tokens -= need
        else:
            status = "reject"

        decisions.append(
            (rid, ts, need, status, f"{req_tokens:.2f}", f"{tok_tokens:.2f}")
        )
        prev_t = ts

    with (out_dir / "decisions.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["id", "timestamp", "tokens", "status", "req_left", "tok_left"])
        writer.writerows(decisions)

    accepted = [row for row in decisions if row[3] == "accept"]
    rejected = [row for row in decisions if row[3] == "reject"]
    summary = {
        "total_requests": len(decisions),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "tokens_served": sum(row[2] for row in accepted),
        "tokens_rejected": sum(row[2] for row in rejected),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
