#!/usr/bin/env python3
"""Decode JWT claims and decide whether each token still grants access."""

import base64
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path


class Malformed(Exception):
    pass


def decode_part(part):
    text = part.replace("-", "+").replace("_", "/")
    text += "=" * (-len(text) % 4)
    try:
        raw = base64.b64decode(text, validate=True)
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise Malformed(str(exc)) from exc
    if not isinstance(value, dict):
        raise Malformed("part is not a JSON object")
    return value


def integer_claim(payload, key):
    """The claim as an int when it is an integer number, else None."""
    value = payload.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value == int(value):
        return int(value)
    return None


def classify(header, payload, now):
    exp = integer_claim(payload, "exp")
    nbf = integer_claim(payload, "nbf")
    if header.get("alg") == "none":
        status = "none-alg"
    elif exp is not None and exp <= now:
        status = "expired"
    elif nbf is not None and nbf > now:
        status = "not-yet-valid"
    else:
        status = "valid"
    subject = payload.get("sub")
    if not isinstance(subject, str):
        subject = ""
    return status, subject, ("" if exp is None else str(exp))


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    now_text = (in_dir / "now.txt").read_text(encoding="utf-8").strip()
    now = int(
        datetime.strptime(now_text, "%Y-%m-%dT%H:%M:%SZ")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )

    rows = []
    subjects = set()
    counts = {"malformed": 0, "none-alg": 0, "expired": 0, "not-yet-valid": 0, "valid": 0}
    index = 0

    for raw_line in (in_dir / "tokens.txt").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        index += 1
        parts = line.split(".")
        if len(parts) != 3:
            continue
        try:
            header = decode_part(parts[0])
            payload = decode_part(parts[1])
        except Malformed:
            counts["malformed"] += 1
            rows.append((str(index), "malformed", "", ""))
            continue
        status, subject, exp = classify(header, payload, now)
        counts[status] += 1
        if subject:
            subjects.add(subject)
        rows.append((str(index), status, subject, exp))

    with (out_dir / "tokens.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["index", "status", "sub", "exp"])
        writer.writerows(rows)

    summary = {
        "tokens": len(rows),
        "malformed": counts["malformed"],
        "none_alg": counts["none-alg"],
        "expired": counts["expired"],
        "not_yet_valid": counts["not-yet-valid"],
        "valid": counts["valid"],
        "subjects": len(subjects),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
