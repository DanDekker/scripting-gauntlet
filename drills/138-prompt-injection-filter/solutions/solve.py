#!/usr/bin/env python3
"""Screen untrusted text for prompt-injection patterns, one verdict per record."""

import json
import os
import re
from pathlib import Path

ZERO_WIDTH = "\u200b\u200c\u200d\ufeff"
ZERO_WIDTH_TABLE = dict.fromkeys(ord(ch) for ch in ZERO_WIDTH)
BASE64 = re.compile(r"(?:base64:|\[base64\])\s*[A-Za-z0-9+/]{16,}", re.IGNORECASE)
EXFILTRATION = re.compile(r"!\[[^\]]*\]\(https?://[^)]*\)", re.IGNORECASE)
DELIMITERS = ("<|im_start|>", "<|im_end|>", "[INST]", "[/INST]", "<<SYS>>", "<</SYS>>")
OVERRIDES = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard all prior",
    "you are now dan",
    "system prompt override",
)
FLAG_ORDER = ("base64-payload", "delimiter-spoof", "exfiltration", "override", "zero-width")


def load_records(path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if not isinstance(obj.get("id"), str) or not isinstance(obj.get("text"), str):
            continue
        source = obj.get("source")
        records.append(
            {
                "id": obj["id"],
                "source": source if isinstance(source, str) else "",
                "text": obj["text"],
            }
        )
    return records


def flags_for(text):
    normalized = text.translate(ZERO_WIDTH_TABLE)
    lowered = normalized.lower()
    found = {
        "base64-payload": bool(BASE64.search(normalized)),
        "delimiter-spoof": any(marker in normalized for marker in DELIMITERS),
        "exfiltration": bool(EXFILTRATION.search(normalized)),
        "override": any(phrase in lowered for phrase in OVERRIDES),
        "zero-width": any(ch in text for ch in ZERO_WIDTH),
    }
    return [flag for flag in FLAG_ORDER if found[flag]]


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    records = load_records(in_dir / "inputs.jsonl")

    rows = []
    counts = {flag: 0 for flag in FLAG_ORDER}
    for record in records:
        flags = flags_for(record["text"])
        for flag in flags:
            counts[flag] += 1
        rows.append(
            (
                record["id"],
                record["source"],
                "flagged" if flags else "clean",
                ";".join(flags),
            )
        )
    rows.sort(key=lambda row: row[0])

    lines = ["id,source,verdict,flags"]
    lines += [",".join(row) for row in rows]
    (out_dir / "screened.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    flagged = sum(1 for row in rows if row[2] == "flagged")
    summary = {
        "total_inputs": len(rows),
        "clean_count": len(rows) - flagged,
        "flagged_count": flagged,
        "by_flag": {flag: counts[flag] for flag in FLAG_ORDER if counts[flag]},
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
