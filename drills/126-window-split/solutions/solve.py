#!/usr/bin/env python3
"""Cut a document into windows that fit a character budget, with an overlap tail."""

import json
import os
import sys
from pathlib import Path


def paragraphs(text):
    """Blank-line separated paragraphs, trailing whitespace stripped, empties dropped."""
    blocks = []
    current = []
    for raw in text.splitlines():
        if not raw.strip():
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(raw.rstrip())
    if current:
        blocks.append(current)

    cleaned = []
    for lines in blocks:
        para = "\n".join(lines).strip()
        if para:
            cleaned.append(para)
    return cleaned


def tail(text, max_chars, overlap):
    if overlap <= 0:
        return ""
    rest = text[-overlap:]
    if len(rest) > max_chars:
        rest = rest[-max_chars:]
    return rest


def windows(paras, max_chars, overlap):
    out = []
    prefix = ""
    index = 0
    count = len(paras)
    while index < count:
        para = paras[index]
        if prefix and len(prefix) + 2 + len(para) > max_chars:
            prefix = ""  # the overlap leaves no room: start clean
        if len(para) > max_chars:
            pieces = [para[at:at + max_chars] for at in range(0, len(para), max_chars)]
            out.extend(pieces)
            index += 1
            prefix = tail(pieces[-1], max_chars, overlap)
            continue
        parts = ([prefix] if prefix else []) + [para]
        index += 1
        while index < count:
            candidate = parts + [paras[index]]
            if len("\n\n".join(candidate)) <= max_chars:
                parts = candidate
                index += 1
            else:
                break
        text = "\n\n".join(parts)
        out.append(text)
        prefix = tail(text, max_chars, overlap)
    return out


def cell(text):
    escaped = text.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '""')
    return '"' + escaped + '"'


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    for name in ("doc.txt", "config.json"):
        if not (in_dir / name).is_file():
            sys.exit(f"missing {in_dir / name}")
    out_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads((in_dir / "config.json").read_text(encoding="utf-8"))
    max_chars = int(config["max_chars"])
    overlap = int(config["overlap"])
    if max_chars <= 0:
        sys.exit(f"config.json: max_chars must be positive, got {max_chars}")

    paras = paragraphs((in_dir / "doc.txt").read_text(encoding="utf-8"))
    chunks = windows(paras, max_chars, overlap)

    lines = ["index,chars,text"]
    for number, text in enumerate(chunks, start=1):
        lines.append(f"{number},{len(text)},{cell(text)}")
    (out_dir / "windows.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "paragraphs": len(paras),
        "windows": len(chunks),
        "chars": sum(len(text) for text in chunks),
        "max_window": max((len(text) for text in chunks), default=0),
        "overlap": overlap,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
