#!/usr/bin/env python3
"""Pull the one valid JSON object/array out of each messy assistant reply."""

import json
import os
import re
from pathlib import Path

HEADER = re.compile(r"^=== RESPONSE (\S+) ===[ \t]*$")
FENCE = re.compile(r"^\s*```(.*)$")
CLOSING = {"{": "}", "[": "]"}


def split_blocks(text):
    """[(id, body)] in document order."""
    blocks = []
    current = None
    for line in text.splitlines():
        header = HEADER.match(line)
        if header:
            current = (header.group(1), [])
            blocks.append(current)
            continue
        if current is not None:
            current[1].append(line)
    return [(name, "\n".join(lines)) for name, lines in blocks]


def fenced_blocks(body):
    """[(language, content)] for every fenced block, in document order."""
    found = []
    language = None
    buffer = []
    for line in body.splitlines():
        fence = FENCE.match(line)
        if language is None:
            if fence:
                language = fence.group(1).strip().lower()
                buffer = []
            continue
        if fence and not fence.group(1).strip():
            found.append((language, "\n".join(buffer)))
            language = None
            buffer = []
            continue
        buffer.append(line)
    if language is not None:
        found.append((language, "\n".join(buffer)))
    return found


def balanced(text, start):
    """The bracketed span beginning at `start`, or None if it never closes."""
    stack = []
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in CLOSING:
            stack.append(CLOSING[char])
        elif char in "}]":
            if not stack or stack[-1] != char:
                return None
            stack.pop()
            if not stack:
                return text[start:index + 1]
    return None


def raw_spans(body):
    for index, char in enumerate(body):
        if char in CLOSING:
            span = balanced(body, index)
            if span is not None:
                yield span


def as_document(text):
    """The parsed value when it is an object or array, else None."""
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, (dict, list)) else None


def extract(body):
    fenced = fenced_blocks(body)
    candidates = [content for language, content in fenced if language == "json"]
    candidates += [content for language, content in fenced if language == ""]
    candidates += list(raw_spans(body))
    for candidate in candidates:
        document = as_document(candidate)
        if document is not None:
            return document
    return None


def main():
    in_dir = Path(os.environ["IN"])
    out_dir = Path(os.environ["OUT"])
    out_dir.mkdir(parents=True, exist_ok=True)

    blocks = split_blocks((in_dir / "responses.txt").read_text(encoding="utf-8"))

    status = ["id,status,type"]
    extracted = []
    objects = arrays = 0

    for name, body in blocks:
        document = extract(body)
        if document is None:
            status.append(f"{name},failed,none")
            continue
        kind = "object" if isinstance(document, dict) else "array"
        if kind == "object":
            objects += 1
        else:
            arrays += 1
        status.append(f"{name},extracted,{kind}")
        extracted.append(
            json.dumps(
                {"id": name, "type": kind, "keys_or_length": len(document), "data": document},
                separators=(",", ":"),
                ensure_ascii=False,
            )
        )

    (out_dir / "extracted.jsonl").write_text(
        "".join(line + "\n" for line in extracted), encoding="utf-8"
    )
    (out_dir / "status.csv").write_text("".join(line + "\n" for line in status), encoding="utf-8")

    total = len(blocks)
    summary = {
        "total_responses": total,
        "extracted_count": objects + arrays,
        "failed_count": total - (objects + arrays),
        "objects_count": objects,
        "arrays_count": arrays,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
