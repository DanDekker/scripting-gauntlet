#!/usr/bin/env python3
"""Chunk markdown docs into paragraphs with stable ids, dropping empties and repeats."""

import json
import os
import re
from pathlib import Path

WHITESPACE = " \t\r\n"
WORD_SPLIT = re.compile(r"[ \t\r\n]+")
PREAMBLE = "(preamble)"


def trim_line(line):
    return line.rstrip(" \t\r")


def paragraphs(path):
    """Yield (section, index, text) for every paragraph slot in the document."""
    lines = path.read_text(encoding="utf-8").split("\n")
    section = PREAMBLE
    buffer = []
    index = 0

    def flush(buffer, section, index):
        text = "\n".join(trim_line(line) for line in buffer).strip(WHITESPACE)
        return section, index + 1, text

    for line in lines:
        if line.startswith("# "):
            if buffer:
                section, index, text = flush(buffer, section, index)
                yield section, index, text
                buffer = []
            section = line[2:].strip(WHITESPACE)
            continue
        if line == "" or line == "\r":
            if buffer:
                section, index, text = flush(buffer, section, index)
                yield section, index, text
                buffer = []
            continue
        buffer.append(line)
    if buffer:
        section, index, text = flush(buffer, section, index)
        yield section, index, text


def count_tokens(text):
    if not text:
        return 0
    return len(WORD_SPLIT.split(text))


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    docs_dir = in_dir / "docs"
    docs = sorted(
        (path for path in docs_dir.iterdir() if path.is_file() and path.name.endswith(".md")),
        key=lambda path: path.name,
    )

    slots = []
    empty_dropped = 0
    for path in docs:
        for section, index, text in paragraphs(path):
            tokens = count_tokens(text)
            if tokens == 0:
                empty_dropped += 1
                continue
            slots.append(
                {
                    "doc": path.name,
                    "section": section,
                    "index": index,
                    "tokens": tokens,
                    "chars": len(text),
                    "text": text,
                }
            )

    seen = set()
    rows = []
    duplicates = 0
    for slot in slots:
        if slot["text"] in seen:
            duplicates += 1
            continue
        seen.add(slot["text"])
        rows.append(slot)

    lines = ["id,doc,section,tokens,chars"]
    for row in rows:
        chunk_id = f"{row['doc']}#{row['section']}#{row['index']}"
        lines.append(
            f"{chunk_id},{row['doc']},{row['section']},{row['tokens']},{row['chars']}"
        )
    (out_dir / "chunks.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "documents": len(docs),
        "total_chunks": len(rows),
        "duplicates_dropped": duplicates,
        "empty_dropped": empty_dropped,
        "tokens": sum(row["tokens"] for row in rows),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
